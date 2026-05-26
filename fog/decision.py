from datetime import datetime, timedelta, timezone

ALERT_WINDOW_SECONDS = 30


def _to_utc(ts):
    if ts is None:
        return None
    if isinstance(ts, datetime):
        return ts if ts.tzinfo else ts.replace(tzinfo=timezone.utc)
    return None


def apply_alert_logic(events):
    """RED if any device emitted an `enter` event in the last 30 seconds, else GREEN."""
    cutoff = datetime.now(timezone.utc) - timedelta(seconds=ALERT_WINDOW_SECONDS)
    for e in events:
        if e.get("label") != "enter":
            continue
        ts = _to_utc(e.get("timestamp"))
        if ts is None:
            continue
        if ts >= cutoff:
            return "RED"
    return "GREEN"
