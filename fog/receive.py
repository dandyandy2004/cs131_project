from firebase_admin import firestore


def watch_events(callback):
    """Attach an on_snapshot listener to the `events` collection.

    Returns a watch handle; call .unsubscribe() to stop.
    """
    db = firestore.client()
    query = (
        db.collection("events")
        .order_by("timestamp", direction=firestore.Query.DESCENDING)
        .limit(50)
    )
    return query.on_snapshot(callback)
