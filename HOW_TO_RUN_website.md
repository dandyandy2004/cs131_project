# How to Run the Public Website

A static, real-time dashboard hosted on **Firebase Hosting**. It reads the
`events` collection from your Firestore via the Firebase Web SDK and shows:

- 🟢 GREEN / 🔴 RED banner (RED if any `enter` event in the last 30 s)
- Latest snapshot (pulled from Cloud Storage public URL)
- Real-time recent-events table (auto-updates via `onSnapshot`)

No build step. No Python. Just static HTML/JS + Firebase Hosting.

---

## What's already done in this repo

| File | Purpose |
|---|---|
| `web/index.html` | Page layout |
| `web/style.css` | Dark theme styling |
| `web/app.js` | Firebase Web SDK + live Firestore listener |
| `web/firebase-config.example.js` | Template for your config |
| `firebase.json` | Tells Firebase Hosting to deploy `web/` |
| `.firebaserc` | Pins the project ID (placeholder) |
| `firestore.rules` | Public read on `events`, no writes from client |

You just need to plug in your credentials and deploy.

---

## Prerequisites

1. **The edge device is already pushing events to Firebase** — see
   `HOW_TO_RUN_edge_dev3.md`. If `events` collection is empty, the page
   will load but show "No events yet."
2. **Node.js installed** (the Firebase CLI is an npm package).
3. **Firebase project exists** in your Google account.

---

## One-time setup (≈ 5 minutes)

### 1. Install the Firebase CLI

```bash
npm install -g firebase-tools
firebase login
```

`firebase login` opens a browser and logs you into the same Google account
that owns your Firebase project.

### 2. Enable Hosting in your Firebase project

Firebase Console → **Hosting** → "Get started" → click through the wizard
(no real work; you can skip the "Install Firebase CLI" step since you just
did it).

### 3. Register a Web app on your project

Firebase Console → **Project Settings** (gear icon) → **Your apps** →
click the **`</>`** icon to register a new Web app.

- Nickname: anything (e.g. `cs131-web`)
- **Do NOT** check "Also set up Firebase Hosting" — we already have it
- After creation, you'll see a `firebaseConfig` object. **Copy it.**

### 4. Plug in your config

Copy the template:

```bash
cp web/firebase-config.example.js web/firebase-config.js
```

Open `web/firebase-config.js` and paste the values from Step 3:

```js
export const firebaseConfig = {
  apiKey: "AIza…",
  authDomain: "your-project.firebaseapp.com",
  projectId: "your-project",
  storageBucket: "your-project.appspot.com",
  messagingSenderId: "123456789",
  appId: "1:123:web:abc…",
};
```

> These values are public — that's fine. Security is enforced by
> `firestore.rules` (read-only for the public, writes only via the
> Admin SDK on the edge device).

### 5. Pin the project ID

Edit `.firebaserc` and replace `REPLACE_WITH_YOUR_PROJECT_ID` with the
`projectId` from your config:

```json
{
  "projects": { "default": "your-project" }
}
```

Or run:

```bash
firebase use --add
```

and pick the project interactively.

---

## Deploy

```bash
firebase deploy --only hosting,firestore:rules
```

Output ends with something like:

```
✔  Deploy complete!

Hosting URL: https://your-project.web.app
```

Open that URL. The page is live and updates in real time as your edge
device writes new events.

---

## Local preview (optional)

To preview without deploying:

```bash
firebase emulators:start --only hosting
```

Opens `http://localhost:5000` serving the same files. Note: this still
talks to your **real** Firestore — the emulator is only for the hosting
layer. To emulate Firestore too, add `firestore` to the `--only` list and
update `app.js` to connect to the emulator (not needed for normal testing).

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `Error: Failed to authenticate, have you run firebase login?` | Run `firebase login` again |
| `HTTP Error: 403, The caller does not have permission` | The Google account in `firebase login` doesn't own the project — log in with the right one (`firebase login --reauth`) |
| Page loads but shows "error: permission-denied" in the footer | `firestore.rules` wasn't deployed — re-run `firebase deploy --only firestore:rules` |
| Image broken icon on snapshots | Cloud Storage blob is not public. `edge_dev3/send.py` calls `blob.make_public()`; if your bucket has *uniform bucket-level access* enabled this is a no-op. Either disable uniform access, or set the bucket-level rule to allow public read on `snapshots/*` |
| `Module not found: firebase-config.js` in browser console | You forgot Step 4 — copy `firebase-config.example.js` to `firebase-config.js` and fill it in |
| Page is blank | Open browser devtools console — most issues surface there |

---

## Handoff checklist for another person

1. Clone repo
2. Run `edge_dev3` once to confirm Firebase writes work (`HOW_TO_RUN_edge_dev3.md`)
3. Steps 1–5 above
4. `firebase deploy`
5. Open the printed URL

That's it. They don't touch any code unless they want to change the layout.
