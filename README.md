
# Sentry 360: 360° Security Camera

**Real-Time 360° Surveillance via Distributed Edge Intelligence**

A distributed edge surveillance system developed for **CS131 – Edge Computing** at the **University of California, Riverside**. The project combines real-time AI inference with cloud services to provide intelligent, low-latency security monitoring while minimizing bandwidth usage. The project architecture and goals are summarized in the accompanying poster.

---

## 📖 Overview

Traditional security systems rely heavily on cloud processing, introducing latency and requiring continuous video streaming. Sentry 360 addresses these issues by performing AI inference directly on edge devices and only sending event information to the cloud.

The system consists of two NVIDIA Jetson Nano devices, each monitoring approximately 180° of coverage, creating a combined 360° surveillance system. YOLOv8 performs person detection locally while InsightFace identifies known blacklisted individuals. Detection events and snapshots are uploaded to Firebase, where a live dashboard updates automatically.

---

## ✨ Features

* Real-time person detection using YOLOv8
* Face recognition with InsightFace
* Blacklist matching
* Event-driven image capture
* Firebase Cloud Storage image uploads
* Firestore event logging
* Live web dashboard
* Distributed edge computing architecture
* Supports multiple edge devices

---

## 🛠 Technologies

### Programming Languages

* Python
* JavaScript
* HTML
* CSS

### AI / Computer Vision

* Ultralytics YOLOv8
* InsightFace
* OpenCV

### Cloud

* Firebase Firestore
* Firebase Cloud Storage
* Firebase Hosting

### Hardware

* NVIDIA Jetson Nano
* USB Webcam
* Raspberry Pi compatible peripherals
* 3D Printed Enclosure

---

## 🏗 System Architecture

```text
USB Camera
      │
      ▼
Jetson Nano Edge Device
      │
      ▼
YOLOv8 Person Detection
      │
      ▼
InsightFace Recognition
      │
      ▼
Blacklist Matching
      │
      ▼
Snapshot Captured
      │
      ├────────► Firebase Storage
      │
      └────────► Firestore Event
                     │
                     ▼
          Live Web Dashboard
```

---

## 📁 Project Structure

```text
cs131_project/
│
├── edge_dev1/
│   ├── main.py
│   ├── detect.py
│   ├── send.py
│   ├── cam.py
│   ├── blacklist.py
│   ├── credentials.json
│   └── snapshots/
│
├── public/
│   ├── index.html
│   ├── app.js
│   ├── style.css
│   └── 404.html
│
├── firebase.json
├── firestore.rules
└── README.md
```

---

## ⚙️ How It Works

1. A Jetson Nano captures live video from a USB camera.
2. YOLOv8 detects people in each frame.
3. InsightFace extracts facial embeddings.
4. Faces are compared against a local blacklist.
5. The system determines whether the scene is **GREEN** or **RED**.
6. A snapshot is taken whenever the system changes state.
7. The snapshot is uploaded to Firebase Cloud Storage.
8. Event information is stored in Firestore.
9. The website automatically updates using Firestore real-time listeners.

---

## 🚨 Event States

### 🟢 GREEN

* No blacklisted individual detected
* Camera area is considered secure

### 🔴 RED

* Blacklisted individual detected
* Snapshot captured
* Image uploaded
* Event logged
* Dashboard updated

---

## 🌐 Live Dashboard

The dashboard displays:

* Current security status
* Latest captured snapshot
* Device ID
* Detection confidence
* Matched identity
* Event timestamp
* Event history

The interface updates automatically whenever a new event is written to Firestore.

---

## ☁️ Firebase

This project uses:

* **Firestore** — stores detection events
* **Cloud Storage** — stores captured snapshots
* **Firebase Hosting** — hosts the live dashboard

Each event contains:

* Device ID
* Event Label
* Security Status
* Confidence Score
* Matched Identity
* Timestamp
* Image URL

---

## 🚀 Installation

Clone the repository:

```bash
git clone https://github.com/dandyandy2004/cs131_project.git
cd cs131_project
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```text
DEVICE_ID=edge_dev1
CAMERA_INDEX=0
INFER_EVERY=3
FIREBASE_CREDENTIALS=credentials.json
FIREBASE_STORAGE_BUCKET=<your-storage-bucket>
```

Run the edge device:

```bash
python main.py
```

Deploy the website:

```bash
firebase deploy
```

---

## 📄 Project Poster

A poster describing the motivation, architecture, implementation, discussion, limitations, and future work is included with this repository.

If you include the PDF in the repository root, you can view it here:
[CS131_Poster_v2_Fixed_Final.pptx (3).pdf](https://github.com/user-attachments/files/31154964/CS131_Poster_v2_Fixed_Final.pptx.3.pdf)

---

## 🎥 Demo Video

Watch the project demonstration:

**https://youtube.com/watch?si=yRmxiuSl9K78ILyG&v=w96mnCS1kAU&feature=youtu.be**

The demonstration includes:

* Real-time person detection
* Blacklist recognition
* RED/GREEN status transitions
* Firebase event logging
* Cloud image uploads
* Live dashboard updates

---

## 🌐 Live Web Application

View the live dashboard here:

**https://cs131-project-496922.web.app/**

The web application displays:

* 🟢 Live RED/GREEN security status
* 📸 Latest captured snapshot
* 📋 Recent detection events
* 👤 Identified blacklist matches
* 📊 Detection confidence
* 🕒 Event timestamps

The dashboard is hosted using **Firebase Hosting** and updates automatically through **Cloud Firestore's real-time listeners**, allowing users to monitor the surveillance system remotely.

---

## 🔮 Future Improvements

* TensorRT optimization
* Multi-camera support
* Person re-identification across cameras
* SMS and email notifications
* Building-wide deployment
* Mobile dashboard
* Historical analytics
* Improved low-light performance

---

## 👥 Team

* Andres Briseno
* Cody Lee
* Henry Lo
* Russell Villanueva

**University of California, Riverside**

**Bourns College of Engineering**

**CS131 – Edge Computing**

Spring 2026

---

## 📚 References

* Ultralytics YOLOv8
* InsightFace
* OpenCV
* Firebase
* NVIDIA Jetson Nano
* Google Firestore
