import { initializeApp } from "firebase/app";
import { getDatabase } from "firebase/database";
import { getFirestore } from "firebase/firestore";
import { getAuth, GoogleAuthProvider, signInWithPopup } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyAk7bxiWJBKRNnt5CWuRLVjCfVKDl8nkGA",
  authDomain: "smart-irrigation-system-f87ad.firebaseapp.com",
  databaseURL: "https://smart-irrigation-system-f87ad-default-rtdb.asia-southeast1.firebasedatabase.app",
  projectId: "smart-irrigation-system-f87ad",
  storageBucket: "smart-irrigation-system-f87ad.appspot.com",
  messagingSenderId: "104415506878",
  appId: "1:104415506878:web:5cdfd3107772c1f76589ef",
};

const app = initializeApp(firebaseConfig);
export const database = getDatabase(app);
export const firestore = getFirestore(app);

// Initialize Firebase Auth
export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();

// Function to sign in with Google
export const signInWithGoogle = () => {
  return signInWithPopup(auth, googleProvider);
};
