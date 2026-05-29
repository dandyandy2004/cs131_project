# Distributed Edge-Based 360° Surveillance System

## Overview
This project implements a distributed edge-computing surveillance system using two NVIDIA Jetson Nanos, each with a 180° camera, to provide full 360° environmental awareness.

Each device performs local person detection and facial recognition against a blacklist of known individuals. A fog coordination layer fuses both devices' results, stitches a combined 360° snapshot on alert, and drives a physical LED indicator. Only meaningful events are sent to the cloud.

---

## Problem
Traditional surveillance systems have:
- Limited camera coverage and blind spots
- High latency from cloud-based processing
- Excessive bandwidth usage from continuous streaming
- Poor real-time response capabilities
- No ability to identify specific known individuals

---

## Solution
Our system uses multiple edge devices that:
- Perform local person detection and facial recognition
- Collaborate to provide 360° coverage
- Send only important events to the cloud
- Generate real-time alert indicators and a combined 360° snapshot

### Alert Logic
- 🟢 GREEN → No blacklisted person detected by either camera
- 🔴 RED → A blacklisted (enrolled) person identified on either camera

Unknown persons are detected and annotated locally but do not trigger a system alert.

---

## System Architecture

### Edge Devices (`edge_dev1/`, `edge_dev2/`)
Each Jetson Nano:
- Captures video via a threaded background frame grabber (`cam.py`)
- Runs YOLOv8n person detection on every 3rd frame (`detect.py`)
- Runs InsightFace (`buffalo_s`) facial recognition and matches against a local blacklist (`blacklist.py`)
- Re-fires an enter event if a previously unknown person is later identified as blacklisted
- Uploads snapshots and event metadata to Firebase on state transitions (`send.py`)

### Fog Layer (`fog/`)
- Listens to both devices' Firestore events in real time (`receive.py`)
- Goes RED only when a blacklisted person is identified on either device (`decision.py`)
- On alert: downloads the latest snapshot from each device, stitches them side-by-side into a 360° JPEG, and uploads to Cloud Storage
- Writes `combined_status/current` and `combined_alerts` to Firestore
- Drives a physical RED/GREEN LED via Jetson GPIO (`main.py`)

### Cloud Service (Firebase)
- Cloud Storage stores individual snapshots and 360° combined images
- Firestore stores per-device events, combined status, and alert history
- Firebase Hosting serves the real-time web dashboard

### Web Dashboard (`web/`)
- Status badge driven by the fog layer's `combined_status/current` decision
- Displays the 360° combined image on blacklist alert
- Event table shows all individual device events in real time

---

## Why Edge Computing?
- Local processing reduces latency
- Less cloud dependency
- Lower bandwidth usage
- Real-time response
- Scalable distributed system

---

## Technologies
- Python 3.8+
- YOLOv8n (Ultralytics) — person detection
- InsightFace `buffalo_s` + ONNX Runtime — facial recognition
- OpenCV — frame capture, annotation, image stitching
- Firebase Admin SDK — cloud upload from edge and fog
- Firebase Web SDK — real-time dashboard (no build step)
- Jetson.GPIO — physical LED output
- NVIDIA Jetson Nano × 2 — edge inference hardware

---

## Future Improvements
- Scale to additional edge devices for larger area coverage
- Mobile push notifications on blacklist alert
- TensorRT optimization for faster inference on Jetson
- Autonomous camera tracking
- Multi-person blacklist tracking across devices

---

## Conclusion
This project demonstrates how distributed edge computing can improve surveillance systems through real-time local processing, collaborative edge intelligence, and efficient cloud integration.
