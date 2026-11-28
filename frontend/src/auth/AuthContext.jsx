import React, { createContext, useState, useEffect, useCallback } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

export const AuthContext = createContext({
  user: null,
  token: null,
  isLoading: true,
  isAuthenticated: false,
  loginWithGoogle: async () => {},
  logout: async () => {},
});

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(() => localStorage.getItem('access_token'));
  const [isLoading, setIsLoading] = useState(true);

  // Helper to fetch current user session from /api/auth/me
  const fetchCurrentUser = useCallback(async (jwtToken) => {
    try {
      const headers = { 'Content-Type': 'application/json' };
      const authToken = jwtToken || localStorage.getItem('access_token');
      if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
      }

      const res = await fetch(`${API_BASE_URL}/api/auth/me`, {
        method: 'GET',
        headers,
        credentials: 'include', // Sends HttpOnly cookie
      });

      if (res.ok) {
        const userData = await res.json();
        setUser(userData);
        return true;
      } else {
        // Cookie or token is invalid/expired
        setUser(null);
        setToken(null);
        localStorage.removeItem('access_token');
        return false;
      }
    } catch (err) {
      console.error('Failed to verify user session:', err);
      setUser(null);
      return false;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Check auth status on mount
  useEffect(() => {
    fetchCurrentUser(token);
  }, [fetchCurrentUser, token]);

  // Google Login exchange handler (waits gracefully if backend is cold-starting)
  const loginWithGoogle = async (credential) => {
    setIsLoading(true);
    try {
      const doLogin = () =>
        fetch(`${API_BASE_URL}/api/auth/google`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ credential }),
        });

      let res;
      try {
        res = await doLogin();
      } catch {
        // Backend may be waking up from sleep — ping /health and retry once
        await fetch(`${API_BASE_URL}/health`).catch(() => {});
        res = await doLogin();
      }

      if (!res.ok) {
        if (res.status === 502 || res.status === 503 || res.status === 504) {
          throw new Error('Backend server is starting up. Please wait a few seconds and try again.');
        }
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Google authentication failed.');
      }

      const data = await res.json();
      const { access_token, user: userData } = data;

      if (access_token) {
        setToken(access_token);
        localStorage.setItem('access_token', access_token);
      }
      setUser(userData);
      return userData;
    } catch (err) {
      if (err?.name === 'TypeError') {
        throw new Error('Backend server is starting up. Please wait a moment and try again.');
      }
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  // Logout handler
  const logout = async () => {
    setIsLoading(true);
    try {
      await fetch(`${API_BASE_URL}/api/auth/logout`, {
        method: 'POST',
        credentials: 'include',
      }).catch(() => {});
    } finally {
      setUser(null);
      setToken(null);
      localStorage.removeItem('access_token');
      setIsLoading(false);
    }
  };

  const value = {
    user,
    token,
    isLoading,
    isAuthenticated: Boolean(user),
    loginWithGoogle,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}
