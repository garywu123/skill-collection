# Tool Compatibility

This is a design baseline, not a substitute for current official documentation.
Recheck the named tool when exact loading behavior materially affects output.

## Canonical strategy

Use root `AGENTS.md` as the cross-tool canonical guidance. Generate adapters only
for consumers that need them.

## Codex

- Reads `AGENTS.md` and supports scoped files along the path from project root to
  the working directory.
- More specific guidance applies closer to the working directory.
- Keep repository facts and workflow guidance in `AGENTS.md`; keep reusable
  task procedures in Skills.

Official documentation:
https://learn.chatgpt.com/docs/agent-configuration/agents-md

## Claude Code

- Reads `CLAUDE.md`, not `AGENTS.md` as its native project file.
- A root `CLAUDE.md` can import the canonical file using `@AGENTS.md`.
- Put Claude-only differences after the import.
- Use `.claude/rules/` for Claude-specific path-scoped rules when needed.

Official documentation:
https://code.claude.com/docs/en/memory

## GitHub Copilot

- Support for `AGENTS.md`, `CLAUDE.md`, and
  `.github/copilot-instructions.md` varies by Copilot surface.
- Prefer `AGENTS.md` when every target surface supports it.
- Create `.github/copilot-instructions.md` for Copilot-specific rules or to
  cover surfaces that do not consume `AGENTS.md`.
- Use `.github/instructions/*.instructions.md` for path-specific Copilot rules.
- Do not assume that an import feature documented for Copilot CLI behaves the
  same in every IDE or GitHub.com surface.

Official support matrix:
https://docs.github.com/en/copilot/reference/custom-instructions-support

## Conflict rule

Do not maintain three independently editable copies of universal project rules.
Keep `AGENTS.md` canonical, make `CLAUDE.md` an import wrapper, and keep any
Copilot-specific file minimal and explicitly derived.
