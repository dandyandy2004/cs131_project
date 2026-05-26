"""Streamlit dashboard for local testing of edge_dev3 events.

Run:
    streamlit run dashboard/app.py

Requires LOCAL_MODE=1 in edge_dev3/.env so events get written to SQLite.
"""
import os
import sqlite3
import time
from datetime import datetime, timedelta

import streamlit as st

_DEFAULT_DB = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "local_data", "events.db")
)
DB_PATH = os.environ.get("LOCAL_DB_PATH", _DEFAULT_DB)
ALERT_WINDOW_SECONDS = 30

st.set_page_config(page_title="cs131 Surveillance — Local", layout="wide")


def fetch_events(limit=50):
    if not os.path.exists(DB_PATH):
        return []
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT * FROM events ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    except sqlite3.OperationalError:
        return []
    finally:
        conn.close()
    return [dict(r) for r in rows]


def alert_status(events):
    cutoff = datetime.now() - timedelta(seconds=ALERT_WINDOW_SECONDS)
    for e in events:
        if e.get("label") != "enter":
            continue
        try:
            ts = datetime.fromisoformat(e["timestamp"])
        except (ValueError, TypeError):
            continue
        if ts >= cutoff:
            return "RED"
    return "GREEN"


st.title("cs131 Surveillance — Local Dashboard")

with st.sidebar:
    st.header("Settings")
    auto_refresh = st.checkbox("Auto-refresh every 2s", value=True)
    st.caption(f"DB path:\n`{DB_PATH}`")
    st.caption(f"DB exists: {os.path.exists(DB_PATH)}")
    if st.button("Refresh now"):
        st.rerun()

events = fetch_events()
status = alert_status(events)

col_status, col_latest = st.columns([1, 2])

with col_status:
    if status == "RED":
        st.error(f"## 🔴 {status}")
        st.caption(f"An ENTER event occurred in the last {ALERT_WINDOW_SECONDS}s.")
    else:
        st.success(f"## 🟢 {status}")
        st.caption(f"No ENTER events in the last {ALERT_WINDOW_SECONDS}s.")

    st.metric("Total events", len(events))
    if events:
        devices = sorted({e["device_id"] for e in events})
        st.metric("Devices reporting", ", ".join(devices))

with col_latest:
    if events:
        latest = events[0]
        st.subheader(
            f"Latest: `{latest['device_id']}` — **{latest['label'].upper()}**"
        )
        st.caption(f"timestamp: {latest['timestamp']}")
        cols = st.columns(3)
        cols[0].metric("Confidence", f"{latest['confidence']:.0%}")
        cols[1].metric("Distance", f"{latest['distance_estimate_ft']:.1f} ft")
        cols[2].metric("Bbox height", f"{latest['bbox_height_px']} px")

        img_path = latest.get("image_path") or ""
        if img_path and os.path.exists(img_path):
            st.image(img_path, caption=os.path.basename(img_path), width=480)
        else:
            st.warning(f"Snapshot file missing: {img_path}")
    else:
        st.info(
            "No events yet. Make sure `edge_dev3/.env` has `LOCAL_MODE=1`, "
            "then run `python edge_dev3/main.py` and trigger an enter/leave "
            "transition (step into the frame, then out)."
        )

st.subheader("Recent events")
if events:
    display_rows = [
        {
            "id": e["id"],
            "device": e["device_id"],
            "label": e["label"],
            "timestamp": e["timestamp"],
            "conf": round(e["confidence"], 3),
            "dist (ft)": round(e["distance_estimate_ft"], 1),
            "bbox h (px)": e["bbox_height_px"],
            "image": os.path.basename(e["image_path"]) if e.get("image_path") else "",
        }
        for e in events
    ]
    st.dataframe(display_rows, use_container_width=True, hide_index=True)
else:
    st.caption("Event table is empty.")

if auto_refresh:
    time.sleep(2)
    st.rerun()
