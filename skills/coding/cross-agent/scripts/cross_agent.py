"""Entry point for the cross-agent CLI bundled with the cross-agent Skill."""

import sys

sys.dont_write_bytecode = True

from crossagent.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
