from datetime import datetime, timezone

STALE_SEC = 300  # treat a device as clear after 5 min of silence


class DeviceTracker:
    def __init__(self):
        self._states = {}  # device_id -> {"blacklisted_present": bool, "updated_at": datetime}

    def update(self, device_id, label, identity):
        """
        Only marks a device RED when a blacklisted person (identity != None) enters.
        Unknown persons entering do not change the combined status to RED.
        """
        self._states[device_id] = {
            "blacklisted_present": label == "enter" and identity is not None,
            "updated_at": datetime.now(timezone.utc),
        }

    def combined_status(self):
        """RED if any non-stale device has a blacklisted person present, else GREEN."""
        now = datetime.now(timezone.utc)
        for state in self._states.values():
            age = (now - state["updated_at"]).total_seconds()
            if age < STALE_SEC and state["blacklisted_present"]:
                return "RED"
        return "GREEN"

    def device_summary(self):
        return {dev: s["blacklisted_present"] for dev, s in self._states.items()}
