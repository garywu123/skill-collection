"""Small, allowlisted observations from provider events; never forward transcripts."""

from __future__ import annotations

from datetime import datetime, timezone


TOKEN_FIELDS = ("input_tokens", "cached_input_tokens", "cache_write_input_tokens",
                "output_tokens", "reasoning_output_tokens")


def token_counts(usage):
    """Only nonnegative provider counters are observations; absent fields stay unknown."""
    return {key: value for key in TOKEN_FIELDS if type(value := (usage or {}).get(key)) is int and value >= 0}


def call_usage(counts, source, status):
    data = {key: counts.get(key) for key in TOKEN_FIELDS}
    data.update(usage_source=source, usage_scope="parent-call", usage_status=status)
    data["total_tokens"] = (data["input_tokens"] + data["output_tokens"]
                            if data["input_tokens"] is not None and data["output_tokens"] is not None else None)
    if status == "reported" and data["total_tokens"] is None:
        data["usage_status"] = "partial"
    return data


def codex_usage(call, totals, source, status):
    """Codex exec reports session totals, including on resume: use a known baseline."""
    totals = token_counts(totals)
    if not totals:
        return
    baseline = call.token_baseline
    delta = {key: value - (baseline.get(key, 0) if baseline is not None else 0)
             for key, value in totals.items()
             if (call.session_id is None or baseline is not None and key in baseline)
             and value >= (baseline.get(key, 0) if baseline is not None else 0)}
    call.telemetry["session_token_usage"] = totals
    call.telemetry["token_usage"] = call_usage(delta, source, status if delta else "unknown")


class Observer:
    def __init__(self, call):
        self.call = call
        self.tasks = {}
        self.started = set()
        self.last_usage = None
        self.claude_inputs = {}
        self.data = call.telemetry
        self.data.update(model=None, effort=None, context_tokens=None, context_limit=None,
                         subagents_requested=None, subagents_started=None, subagents_active=None, compactions=0)

    def emit(self, event, **details):
        if event == "usage":
            if self.data == self.last_usage:
                return
            self.last_usage = dict(self.data)
        if self.call.progress:
            self.call.progress({"event": event, "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                                "telemetry": dict(self.data), **details})

    def observe(self, event):
        if not isinstance(event, dict):
            return
        kind = event.get("type")
        subtype = event.get("subtype")
        if kind == "turn_context":
            payload = event.get("payload") or {}
            self.data["model"] = payload.get("model")
            self.data["effort"] = payload.get("effort")
            self.emit("runtime")
        elif kind == "event_msg" and (event.get("payload") or {}).get("type") == "token_count":
            info = event["payload"].get("info") or {}
            self.data["context_tokens"] = (info.get("last_token_usage") or {}).get("input_tokens")
            self.data["context_limit"] = info.get("model_context_window")
            if info.get("total_token_usage") and (self.data.get("token_usage") or {}).get("usage_status") != "reported":
                codex_usage(self.call, info["total_token_usage"], "codex-rollout-delta", "partial")
            self.emit("usage")
        elif kind == "turn.completed":
            codex_usage(self.call, event.get("usage"), "codex-session-delta", "reported")
            self.emit("usage")
        elif kind == "compacted":
            self.data["compactions"] += 1
            self.data["context_tokens"] = None
            self.emit("compaction", source="provider")
        elif kind == "system" and subtype == "init":
            self.data["session_id"] = event.get("session_id")
            self.data["model"] = event.get("model")
            self.data["effort"] = event.get("effort")
            self.emit("worker-ready", session_id=event.get("session_id"))
        elif kind == "thread.started":
            self.data["session_id"] = event.get("thread_id")
            self.emit("worker-ready", session_id=event.get("thread_id"))
        elif kind == "system" and subtype in ("compact_boundary", "microcompact_boundary"):
            self.data["compactions"] += 1
            self.data["context_tokens"] = None
            self.emit("compaction", source="provider")
        elif kind == "system" and subtype in ("task_started", "task_notification"):
            task_id = event.get("task_id")
            if task_id and (event.get("task_type") == "local_agent" or task_id in self.tasks):
                self.tasks[task_id] = subtype == "task_started"
                self.data["subagents_started"] = len(self.tasks)
                self.data["subagents_active"] = sum(self.tasks.values())
                self.emit("subagent-started" if self.tasks[task_id] else "subagent-finished", task_id=task_id)
        elif kind == "assistant":
            message = event.get("message") or {}
            # Child usage must never replace the parent worker's context measurement.
            if not event.get("parent_tool_use_id"):
                usage = message.get("usage") or {}
                keys = ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")
                if any(key in usage for key in keys):
                    self.data["context_tokens"] = sum(usage.get(key) or 0 for key in keys)
                if message.get("model") and message["model"] != "<synthetic>":
                    self.data["model"] = message["model"]
                # Several tool blocks share one API message ID. Input/cache counts are
                # recoverable on timeout; assistant output counts are placeholders.
                if message.get("id") and type(usage.get("input_tokens")) is int:
                    self.claude_inputs[message["id"]] = {
                        "input_tokens": sum(usage.get(key) or 0 for key in keys),
                        "cached_input_tokens": usage.get("cache_read_input_tokens", 0),
                        "cache_write_input_tokens": usage.get("cache_creation_input_tokens", 0),
                    }
                    counts = {key: sum(row[key] for row in self.claude_inputs.values())
                              for key in ("input_tokens", "cached_input_tokens", "cache_write_input_tokens")}
                    self.data["token_usage"] = call_usage(counts, "claude-assistant-inputs", "partial")
            for block in message.get("content") or []:
                if block.get("type") != "tool_use":
                    continue
                name = block.get("name")
                if name in ("Agent", "Task") and block.get("id") not in self.started:
                    self.started.add(block.get("id"))
                    self.data["subagents_requested"] = len(self.started)
                    self.emit("subagent-requested", tool=name)
                elif name in ("Read", "Grep", "Glob", "Edit", "Write", "Bash", "PowerShell"):
                    self.emit("activity", tool=name)
            self.emit("usage")
        elif kind in ("item.started", "item.completed"):
            item = event.get("item") or {}
            item_kind = item.get("type")
            if item_kind in ("command_execution", "file_change", "mcp_tool_call", "web_search", "todo_list"):
                self.emit("activity", tool=item_kind, status=item.get("status"))
            elif item_kind == "collab_tool_call":
                # Count distinct receivers of spawn calls, not send/wait operations.
                if item.get("tool") == "spawn_agent" and kind == "item.completed":
                    self.started.update(item.get("receiver_thread_ids") or [])
                    self.data["subagents_started"] = len(self.started)
                    self.emit("subagent-started")
        elif kind == "result":
            usage = event.get("usage") or {}
            if "input_tokens" in token_counts(usage) and event.get("subtype") != "error_during_execution":
                counts = token_counts(usage)
                counts["input_tokens"] += (usage.get("cache_read_input_tokens") or 0) + (usage.get("cache_creation_input_tokens") or 0)
                counts["cached_input_tokens"] = usage.get("cache_read_input_tokens", 0)
                counts["cache_write_input_tokens"] = usage.get("cache_creation_input_tokens", 0)
                self.data["token_usage"] = call_usage(counts, "claude-result", "partial" if event.get("is_error") else "reported")
                self.emit("usage")
            stats = event.get("subagent_stats")
            if isinstance(stats, dict):
                self.data["subagents_started"] = stats.get("spawned")
                # Final aggregate does not prove how many children are currently active.
                self.emit("subagent-summary")
