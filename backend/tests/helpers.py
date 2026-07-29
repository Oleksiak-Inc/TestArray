from uuid import uuid4


def _uid() -> str:
    """Return a short unique hex string for tests."""
    return uuid4().hex[:8]
