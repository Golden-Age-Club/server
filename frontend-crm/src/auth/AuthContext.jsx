/* eslint-disable react-refresh/only-export-components */
import React, { createContext, useContext, useMemo, useState, useEffect } from "react";
import { authAPI } from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Check if user is already logged in on mount
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      // Verify token and get user info
      authAPI.getCurrentUser()
        .then((response) => {
          if (response.success && response.data) {
            setUser(response.data);
          }
        })
        .catch(() => {
          // Token invalid, clear storage
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
        })
        .finally(() => {
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (username, password) => {
    const response = await authAPI.login(username, password);
    if (response.success && response.data) {
      setUser(response.data.user);
    }
    return response;
  };

  const logout = async () => {
    await authAPI.logout();
    setUser(null);
  };

  const value = useMemo(() => {
    return {
      user,
      role: user?.role,
      permissions: user?.permissions ?? [],
      isAuthed: !!user,
      loading,
      login,
      logout,
      setUser, // For updating user after profile changes
    };
  }, [user, loading]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
