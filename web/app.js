// Real-time dashboard — status driven by fog layer, events table from edge devices.
// Uses the Firebase Web SDK directly from the CDN — no build step.

import { initializeApp } from "https://www.gstatic.com/firebasejs/10.13.2/firebase-app.js";
import {
  getFirestore,
  collection,
  doc,
  query,
  orderBy,
  limit,
  onSnapshot,
} from "https://www.gstatic.com/firebasejs/10.13.2/firebase-firestore.js";
import { firebaseConfig } from "./firebase-config.js";

const EVENT_LIMIT = 50;

const app = initializeApp(firebaseConfig);
const db  = getFirestore(app);

const statusEl     = document.getElementById("status");
const latestImgEl  = document.getElementById("latest-img");
const latestMetaEl = document.getElementById("latest-meta");
const tableBodyEl  = document.querySelector("#events tbody");
const connStatusEl = document.getElementById("conn-status");

function tsToDate(ts) {
  if (!ts) return null;
  if (typeof ts.toDate === "function") return ts.toDate();
  if (typeof ts === "string" || typeof ts === "number") return new Date(ts);
  return null;
}

function fmtTime(d) {
  return d ? d.toLocaleString() : "—";
}

// ── Status badge — driven by fog/combined_status/current ──────────────────────
onSnapshot(
  doc(db, "combined_status", "current"),
  (docSnap) => {
    if (!docSnap.exists()) return;
    const data = docSnap.data();
    const red  = data.status === "RED";

    statusEl.textContent = red ? "🔴 RED" : "🟢 GREEN";
    statusEl.className   = red ? "red"    : "green";

    // Show 360° combined image when a blacklist hit fires
    if (data.combined_image_url) {
      latestImgEl.src = data.combined_image_url;
      const identity  = data.identity ?? "unknown";
      const devices   = Object.entries(data.devices ?? {})
        .map(([d, v]) => `${d}: ${v ? "RED" : "GREEN"}`)
        .join(", ");
      latestMetaEl.innerHTML = `
        <div><strong>360° Combined View</strong></div>
        <div>${fmtTime(tsToDate(data.timestamp))}</div>
        <div>Identity: <strong>${identity}</strong></div>
        <div>${devices}</div>
      `;
    }
  },
  (err) => console.error("[combined_status]", err),
);

// ── Events table — all individual device events ───────────────────────────────
function renderTable(events) {
  tableBodyEl.innerHTML = "";
  for (const e of events) {
    const tr       = document.createElement("tr");
    const conf     = ((e.confidence ?? 0) * 100).toFixed(0);
    const identity = e.identity ?? "—";
    tr.innerHTML = `
      <td>${e.device_id ?? ""}</td>
      <td>${e.label ?? ""}</td>
      <td>${fmtTime(tsToDate(e.timestamp))}</td>
      <td>${conf}%</td>
      <td>${identity}</td>
    `;
    tableBodyEl.appendChild(tr);
  }
}

onSnapshot(
  query(collection(db, "events"), orderBy("timestamp", "desc"), limit(EVENT_LIMIT)),
  (snapshot) => {
    renderTable(snapshot.docs.map((d) => d.data()));
    connStatusEl.textContent = `live · ${snapshot.size} events`;
  },
  (err) => {
    console.error("Firestore listener error:", err);
    connStatusEl.textContent = `error: ${err.code || err.message}`;
  },
);
