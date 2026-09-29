"""Small, allowlisted observations from provider events; never forward transcripts."""

from __future__ import annotations

from datetime import datetime, timezone


class Observer:
    def __init__(self, call):
        self.call = call
        self.tasks = {}
        self.started = set()
        self.last_usage = None
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
            self.emit("usage")
        elif kind == "compacted":
            self.data["compactions"] += 1
            self.data["context_tokens"] = None
            self.emit("compaction", source="provider")
        elif kind == "system" and subtype == "init":
            self.data["model"] = event.get("model")
            self.data["effort"] = event.get("effort")
            self.emit("worker-ready", session_id=event.get("session_id"))
        elif kind == "thread.started":
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
            stats = event.get("subagent_stats")
            if isinstance(stats, dict):
                self.data["subagents_started"] = stats.get("spawned")
                # Final aggregate does not prove how many children are currently active.
                self.emit("subagent-summary")
