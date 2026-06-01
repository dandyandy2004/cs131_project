
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";

import {
  getFirestore,
  collection,
  query,
  orderBy,
  onSnapshot
} from "https://www.gstatic.com/firebasejs/10.12.2/firebase-firestore.js";

const firebaseConfig = {
  apiKey: "AIzaSyCTf4qvDWtQWuhzTRD2w7yqse4VDN-eTNU",
  authDomain: "cs131-project-496922.firebaseapp.com",
  projectId: "cs131-project-496922",
  storageBucket: "cs131-project-496922.firebasestorage.app",
};

const app = initializeApp(firebaseConfig);

const db = getFirestore(app);

const statusBox = document.getElementById("status");

const latestImg = document.getElementById("latest-img");

const latestMeta = document.getElementById("latest-meta");

const tbody = document.querySelector("#events tbody");

const connStatus = document.getElementById("conn-status");

console.log("tbody found:", tbody);

const q = query(
  collection(db, "events"),
  orderBy("timestamp", "desc")
);

onSnapshot(q, (snapshot) => {

  console.log("snapshot size:", snapshot.size);

  connStatus.textContent = "connected";

  tbody.innerHTML = "";

  const docsWithImages = snapshot.docs.filter((doc) => {

    const data = doc.data();

    return data.image_url && data.image_url.trim() !== "";
  });

  console.log("docs with images:", docsWithImages.length);

  if (docsWithImages.length === 0) {

    latestMeta.textContent = "No snapshot events found.";

    latestImg.style.display = "none";

    return;
  }

  const latest = docsWithImages[0].data();

  const status = String(
    latest.status || "green"
  ).toLowerCase();

  console.log("latest status:", status);

  if (status === "red") {

    statusBox.textContent = "🔴 RED";

    statusBox.className = "red";

  } else {

    statusBox.textContent = "🟢 GREEN";

    statusBox.className = "green";
  }

  latestImg.src = latest.image_url;

  latestImg.style.display = "block";

  const latestTime = latest.timestamp?.seconds
    ? new Date(
        latest.timestamp.seconds * 1000
      ).toLocaleString()
    : "No time";

  latestMeta.innerHTML = `
    <b>Device:</b> ${latest.device_id || "unknown"}<br>
    <b>Label:</b> ${latest.label || "unknown"}<br>
    <b>Status:</b> ${status}<br>
    <b>Identity:</b> ${latest.identity || "unknown"}<br>
    <b>Time:</b> ${latestTime}
  `;

  docsWithImages.forEach((doc) => {

    const data = doc.data();

    const time = data.timestamp?.seconds
      ? new Date(
          data.timestamp.seconds * 1000
        ).toLocaleString()
      : "No time";

    tbody.innerHTML += `
      <tr>
        <td>${data.device_id || "unknown"}</td>
        <td>${data.label || "unknown"}</td>
        <td>${time}</td>
        <td>${data.confidence ?? "N/A"}</td>
        <td>${data.identity || "unknown"}</td>
      </tr>
    `;
  });

}, (error) => {

  console.error("Firestore error:", error);

  connStatus.textContent = "Firestore error";

  latestMeta.textContent = error.message;
});

