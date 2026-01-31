import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export default function SignIn() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await login(username, password);
      navigate("/");
    } catch (err) {
      setError(err.message || "Login failed. Please check your credentials.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-100 dark:bg-gray-950">
      <div className="mx-auto w-full max-w-md rounded-lg bg-white p-8 shadow-md dark:bg-gray-800">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Sign In</h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Sign in to access the admin dashboard
        </p>

        {error && (
          <div className="mt-4 rounded-lg bg-red-50 p-4 text-sm text-red-800 dark:bg-red-900/20 dark:text-red-400">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="mt-6 space-y-3">
          <input
            className="w-full rounded-lg border border-gray-300 bg-gray-50 px-4 py-3 outline-none focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 dark:border-gray-700 dark:bg-gray-900 dark:text-white"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            autoComplete="username"
          />
          <input
            className="w-full rounded-lg border border-gray-300 bg-gray-50 px-4 py-3 outline-none focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 dark:border-gray-700 dark:bg-gray-900 dark:text-white"
            placeholder="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            autoComplete="current-password"
          />
          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-orange-500 px-4 py-3 font-medium text-white hover:bg-orange-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? "Signing in..." : "Sign In"}
          </button>
        </form>

        <div className="mt-6 text-center text-sm text-gray-600 dark:text-gray-400">
          <p>Default credentials:</p>
          <p className="font-mono">superadmin / ChangeMe123!</p>
        </div>
      </div>
    </div>
  );
}
