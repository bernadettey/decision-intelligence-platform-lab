from hashlib import sha256


def deterministic_id(*parts: object, prefix: str | None = None, length: int = 16) -> str:
    """Return a stable logical identifier for replay-sensitive generated records."""

    if length < 8 or length > 64:
        raise ValueError("length must be between 8 and 64")

    normalized = "|".join(str(part) for part in parts)
    digest = sha256(normalized.encode("utf-8")).hexdigest()[:length]
    return f"{prefix}_{digest}" if prefix else digest
