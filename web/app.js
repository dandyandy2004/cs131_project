// Real-time view of the `events` Firestore collection written by edge_dev3.
// Uses the Firebase Web SDK directly from the CDN — no build step.

import { initializeApp } from "https://www.gstatic.com/firebasejs/10.13.2/firebase-app.js";
import {
  getFirestore,
  collection,
  query,
  orderBy,
  limit,
  onSnapshot,
} from "https://www.gstatic.com/firebasejs/10.13.2/firebase-firestore.js";
import { firebaseConfig } from "./firebase-config.js";

const ALERT_WINDOW_MS = 30_000;
const EVENT_LIMIT = 50;

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

const statusEl = document.getElementById("status");
const latestImgEl = document.getElementById("latest-img");
const latestMetaEl = document.getElementById("latest-meta");
const tableBodyEl = document.querySelector("#events tbody");
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

function renderStatus(events) {
  const cutoff = Date.now() - ALERT_WINDOW_MS;
  const red = events.some((e) => {
    if (e.label !== "enter") return false;
    const d = tsToDate(e.timestamp);
    return d && d.getTime() >= cutoff;
  });
  statusEl.textContent = red ? "🔴 RED" : "🟢 GREEN";
  statusEl.className = red ? "red" : "green";
}

function renderLatest(events) {
  if (!events.length) {
    latestImgEl.removeAttribute("src");
    latestMetaEl.textContent = "No events yet.";
    return;
  }
  const e = events[0];
  if (e.image_url) {
    latestImgEl.src = e.image_url;
  } else {
    latestImgEl.removeAttribute("src");
  }
  const conf = ((e.confidence ?? 0) * 100).toFixed(0);
  const identity = e.identity ?? "unknown";
  latestMetaEl.innerHTML = `
    <div><strong>${e.device_id ?? "?"}</strong> — ${(e.label ?? "?").toUpperCase()}</div>
    <div>${fmtTime(tsToDate(e.timestamp))}</div>
    <div>Confidence: ${conf}%</div>
    <div>Identity: ${identity}</div>
  `;
}

function renderTable(events) {
  tableBodyEl.innerHTML = "";
  for (const e of events) {
    const tr = document.createElement("tr");
    const conf = ((e.confidence ?? 0) * 100).toFixed(0);
    const identity = e.identity ?? "unknown";
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

const q = query(
  collection(db, "events"),
  orderBy("timestamp", "desc"),
  limit(EVENT_LIMIT),
);

onSnapshot(
  q,
  (snapshot) => {
    const events = snapshot.docs.map((d) => d.data());
    renderStatus(events);
    renderLatest(events);
    renderTable(events);
    connStatusEl.textContent = `live · ${events.length} events`;
  },
  (err) => {
    console.error("Firestore listener error:", err);
    connStatusEl.textContent = `error: ${err.code || err.message}`;
  },
);
