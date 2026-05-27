// Copy this file to `firebase-config.js` in the same folder and paste
// in your Firebase web app's config object.
//
// Find it at: Firebase Console -> Project Settings -> Your apps ->
//             Web app -> SDK setup and configuration -> Config
//
// These values are PUBLIC and safe to commit (security is enforced by
// Firestore rules in firestore.rules). The `firebase-config.js` file is
// gitignored only so each contributor can deploy to their own project
// without stepping on each other's configs.

export const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_PROJECT.firebaseapp.com",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_PROJECT.appspot.com",
  messagingSenderId: "YOUR_SENDER_ID",
  appId: "YOUR_APP_ID",
};
