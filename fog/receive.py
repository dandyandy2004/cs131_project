def start_listener(db, on_event):
    """
    Opens a real-time Firestore listener on the `events` collection.
    - First callback: bootstraps state from the most recent event per device.
    - Subsequent callbacks: calls on_event(device_id, label, identity, image_url)
      for each newly added document.
    Returns the unsubscribe callable.
    """
    _initialized = [False]
    col_ref = db.collection("events")

    def _callback(col_snapshot, changes, _read_time):
        if not _initialized[0]:
            # Seed current state from the latest event per device
            by_device = {}
            for doc in col_snapshot.documents:
                data = doc.to_dict()
                dev = data.get("device_id")
                ts = data.get("timestamp")
                if not dev or not ts:
                    continue
                if dev not in by_device or ts > by_device[dev]["ts"]:
                    by_device[dev] = {
                        "ts": ts,
                        "label": data.get("label"),
                        "identity": data.get("identity"),
                        "image_url": data.get("image_url"),
                    }
            for dev, info in by_device.items():
                if info["label"]:
                    print(f"[fog] bootstrap {dev} -> {info['label']} identity={info['identity']}")
                    on_event(dev, info["label"], info.get("identity"), info.get("image_url"))
            _initialized[0] = True
            return

        for change in changes:
            if change.type.name != "ADDED":
                continue
            data = change.document.to_dict()
            dev = data.get("device_id")
            label = data.get("label")
            if dev and label:
                on_event(dev, label, data.get("identity"), data.get("image_url"))

    return col_ref.on_snapshot(_callback)
