from datetime import datetime, timezone


def agora_utc() -> datetime:
    return datetime.now(timezone.utc)
