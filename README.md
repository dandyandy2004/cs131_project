# Distributed Edge-Based 360° Surveillance System

## Overview
This project implements a distributed edge-computing surveillance system using two coordinated edge devices with 180° cameras to provide full 360° environmental awareness.

The system performs local object/human detection on each device and combines results to generate real-time alerts with minimal cloud dependency.

---

## Problem
Traditional surveillance systems have:
- Limited camera coverage and blind spots
- High latency from cloud-based processing
- Excessive bandwidth usage from continuous streaming
- Poor real-time response capabilities

---

## Solution
Our system uses multiple edge devices that:
- Perform local object detection
- Collaborate to provide 360° coverage
- Send only important events to the cloud
- Generate real-time alert indicators

### Alert Logic
- 🟢 GREEN → No objects detected
- 🔴 RED → Object or human detected

---

## System Architecture

### Edge Device 1 & 2
Each device:
- Captures video feed
- Runs local object detection
- Sends detection results to coordination layer

### Coordination Layer
- Combines detection results
- Triggers RED/GREEN status

### Cloud Service
- Stores event logs and detection data
- Provides monitoring dashboard

---

## Why Edge Computing?
- Local processing reduces latency
- Less cloud dependency
- Lower bandwidth usage
- Real-time response
- Scalable distributed system

---

## Technologies
- Python
- OpenCV
- YOLO Object Detection
- Edge Devices (Raspberry Pi / Jetson Nano)
- MQTT / Socket Communication

---

## Future Improvements
- Multi-camera scaling
- AI threat classification
- Mobile notifications
- Real-time dashboard
- Autonomous tracking

---

## Conclusion
This project demonstrates how distributed edge computing can improve surveillance systems through real-time local processing, collaborative edge intelligence, and efficient cloud integration.
