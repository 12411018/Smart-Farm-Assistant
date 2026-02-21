import React, { createContext, useState, useEffect, useContext } from 'react';
import { auth } from '../firebase';
import { 
  onAuthStateChanged, 
  signInAnonymously,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut as firebaseSignOut
} from 'firebase/auth';

const AuthContext = createContext();

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }) {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Sign in anonymously for users who don't want to create an account
  const signInAnonymous = async () => {
    try {
      const result = await signInAnonymously(auth);
      return result.user;
    } catch (error) {
      console.error('Error signing in anonymously:', error);
      throw error;
    }
  };

  // Sign in with email and password
  const signIn = async (email, password) => {
    try {
      const result = await signInWithEmailAndPassword(auth, email, password);
      return result.user;
    } catch (error) {
      console.error('Error signing in:', error);
      throw error;
    }
  };

  // Create account with email and password
  const signUp = async (email, password) => {
    try {
      const result = await createUserWithEmailAndPassword(auth, email, password);
      return result.user;
    } catch (error) {
      console.error('Error signing up:', error);
      throw error;
    }
  };

  // Sign out
  const signOut = async () => {
    try {
      await firebaseSignOut(auth);
    } catch (error) {
      console.error('Error signing out:', error);
      throw error;
    }
  };

  // Get user ID for chat storage
  const getUserId = () => {
    if (currentUser) {
      // Use Firebase UID as the user identifier
      return currentUser.uid;
    }
    // Fallback to localStorage for temporary identification
    let tempUserId = localStorage.getItem('temp_user_id');
    if (!tempUserId) {
      tempUserId = `temp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem('temp_user_id', tempUserId);
    }
    return tempUserId;
  };

  // Get user display info
  const getUserDisplayName = () => {
    if (currentUser) {
      if (currentUser.isAnonymous) {
        return 'Guest User';
      }
      return currentUser.email || currentUser.displayName || 'User';
    }
    return 'Guest';
  };

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setCurrentUser(user);
      setLoading(false);
      
      // If user logged in, clear temporary user ID
      if (user && !user.isAnonymous) {
        localStorage.removeItem('temp_user_id');
      }
    });

    return unsubscribe;
  }, []);

  const value = {
    currentUser,
    signInAnonymous,
    signIn,
    signUp,
    signOut,
    getUserId,
    getUserDisplayName,
    isAuthenticated: !!currentUser,
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
}
