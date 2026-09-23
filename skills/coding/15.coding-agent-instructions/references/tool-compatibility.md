# Tool Compatibility

This is a design baseline, not a substitute for current official documentation.
Recheck the named tool when exact loading behavior materially affects output.

## Canonical strategy

Keep the root `AGENTS.md` canonical across tools. Generate an adapter only for a
consumer that needs one, and keep every adapter derived and minimal.

## Codex

- Reads `AGENTS.md` and supports scoped files along the path from the project
  root to the working directory.
- More specific guidance applies closer to the working directory.
- Add a nested `AGENTS.md` only for a subtree with materially different commands
  or constraints.

Official documentation:
https://learn.chatgpt.com/docs/agent-configuration/agents-md

## Claude Code

- Reads `CLAUDE.md` as its native project file, not `AGENTS.md`.
- A root `CLAUDE.md` can import the canonical file with `@AGENTS.md` on its own
  line. Put Claude-only differences after the import.
- Use `.claude/rules/` for Claude-specific path-scoped rules when needed.

Official documentation:
https://code.claude.com/docs/en/memory

## GitHub Copilot

- Support for `AGENTS.md`, `CLAUDE.md`, and `.github/copilot-instructions.md`
  varies by Copilot surface.
- Create `.github/copilot-instructions.md` for Copilot-specific rules and for
  surfaces that do not consume `AGENTS.md`.
- Use `.github/instructions/*.instructions.md` for path-specific Copilot rules.
- Do not assume that an import feature documented for one Copilot surface
  behaves the same in every IDE or on GitHub.com.

Official support matrix:
https://docs.github.com/en/copilot/reference/custom-instructions-support

## Conflict rule

Never maintain three independently editable copies of a universal project rule.
Keep `AGENTS.md` canonical, make `CLAUDE.md` an import wrapper, and keep any
Copilot file minimal and explicitly derived.
