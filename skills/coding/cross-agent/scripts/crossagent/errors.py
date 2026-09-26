"""Errors the CLI reports without advancing a run."""


class UsageError(Exception):
    """A request the CLI refuses; run state stays unchanged."""


class GitError(Exception):
    """A Git command failed."""
