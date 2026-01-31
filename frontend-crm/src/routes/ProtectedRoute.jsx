import React from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export default function ProtectedRoute({ requiredPermission, children }) {
  const { isAuthed, permissions } = useAuth();

  if (!isAuthed) return <Navigate to="/auth/sign-in" replace />;

  if (requiredPermission && !permissions.includes(requiredPermission)) {
    return <Navigate to="/403" replace />;
  }

  return children;
}

