import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showAuthModal, setShowAuthModal] = useState(false);

  // Load user from localStorage on mount
  useEffect(() => {
    const savedToken = localStorage.getItem('auth_token');
    const savedUser = localStorage.getItem('auth_user');
    
    if (savedToken && savedUser) {
      setToken(savedToken);
      setUser(JSON.parse(savedUser));
    }
    
    setLoading(false);
  }, []);

  const signup = async (username, email, password) => {
    try {
      const response = await fetch('http://127.0.0.1:8000/auth/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Signup failed');
      }

      const data = await response.json();
      setToken(data.access_token);
      setUser(data.user);
      
      localStorage.setItem('auth_token', data.access_token);
      localStorage.setItem('auth_user', JSON.stringify(data.user));
      
      return data;
    } catch (error) {
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

  const signin = async (email, password) => {
    try {
      const response = await fetch('http://127.0.0.1:8000/auth/signin', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Signin failed');
      }

      const data = await response.json();
      setToken(data.access_token);
      setUser(data.user);
      
      localStorage.setItem('auth_token', data.access_token);
      localStorage.setItem('auth_user', JSON.stringify(data.user));
      
      return data;
    } catch (error) {
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

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('auth_token');
    localStorage.removeItem('auth_user');
  };

  const value = {
    user,
    token,
    loading,
    showAuthModal,
    setShowAuthModal,
    signup,
    signin,
    logout,
    isAuthenticated: !!token && !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
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
