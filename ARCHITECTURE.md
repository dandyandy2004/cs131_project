# Architecture

Three-tier distributed surveillance system: edge devices run local
detection and push events to Firebase; the fog layer subscribes to those
events and produces aggregate alerts.

---

## Tiers

### 1. Edge (`edge_dev3/`)
- Captures from a local camera (`cv2.VideoCapture`).
- Runs YOLOv8 nano (`yolov8n.pt`) locally, filtered to class 0 (person).
- Computes a monocular distance estimate per detection in `detect.py`:

  `distance_m = (KNOWN_PERSON_HEIGHT_M * FOCAL_LENGTH_PX) / bbox_height_px`

- On every GREEN↔RED transition: saves a local JPEG, then uploads to
  Firebase Cloud Storage and writes a Firestore event document.

`edge_dev1/` and `edge_dev2/` exist as **isolated placeholders** — empty
stub files reserved for future independent implementations. They are not
wired into the system today.

### 2. Cloud (Firebase)
- **Cloud Storage** bucket holds snapshots under `snapshots/<label>_<ts>.jpg`.
- **Firestore** collection `events` holds one document per transition with
  fields: `device_id`, `label`, `timestamp` (server time), `image_url`,
  `confidence`, `bbox_height_px`, `distance_estimate_m`.

### 3. Fog (`fog/`)
- `receive.py` attaches a Firestore `on_snapshot` listener to the `events`
  collection (latest 50, ordered by timestamp desc).
- `decision.py` exposes `apply_alert_logic(events)` — returns `"RED"` if any
  `enter` event occurred within the last 30 seconds, else `"GREEN"`.
- `main.py` wires the listener to the decision function and prints each new
  event plus the resulting alert status.

---

## Data Flow

```
                          ┌──────────────┐
                          │  edge_dev3   │
                          │  cam→detect  │
                          │   ↓ transit. │
                          │   save jpg   │
                          └──────┬───────┘
                                 │ upload
                                 ▼
 ┌─────────────────────────────────────────────────────┐
 │              Firebase Cloud Storage                 │
 │           snapshots/<label>_<ts>.jpg                │
 └─────────────────────────────────────────────────────┘
        │ image_url                                    
        ▼                                              
 ┌─────────────────────────────────────────────────────┐
 │              Firestore: events/                     │
 │   { device_id, label, timestamp, image_url,         │
 │     confidence, bbox_height_px,                     │
 │     distance_estimate_m }                           │
 └────────────────────────┬────────────────────────────┘
                          │ on_snapshot stream
                          ▼
                ┌──────────────────────┐
                │        fog/         │
                │  receive → decision │
                │  → GREEN / RED      │
                └──────────────────────┘
```

---

## Environment Variables

### Edge device (`edge_dev3/.env`)
| Var | Required | Default | Purpose |
|---|---|---|---|
| `FIREBASE_CREDENTIALS` | yes | `firebase_credentials.json` | Path to service account JSON |
| `FIREBASE_STORAGE_BUCKET` | yes | — | Cloud Storage bucket name (e.g. `your-project.appspot.com`) |
| `DEVICE_ID` | recommended | `edge_dev3` | String written to each Firestore event |
| `CAMERA_INDEX` | no | `0` | OpenCV camera index |

### Fog (`fog/.env`)
| Var | Required | Default | Purpose |
|---|---|---|---|
| `FIREBASE_CREDENTIALS` | yes | `firebase_credentials.json` | Path to service account JSON |
| `FIREBASE_STORAGE_BUCKET` | optional | — | Only needed if the fog process fetches images |

---

## Distance Estimation

All distance math lives in `edge_dev3/detect.py`. Two tunables:

- `FOCAL_LENGTH_PX = 600.0` — placeholder; calibrate per camera.
- `KNOWN_PERSON_HEIGHT_M = 1.70` — assumed average human height.

Calibration procedure (future work): place a person of known height at a
measured distance, observe `bbox_height_px`, solve
`FOCAL_LENGTH_PX = (distance_m * bbox_height_px) / KNOWN_PERSON_HEIGHT_M`.
