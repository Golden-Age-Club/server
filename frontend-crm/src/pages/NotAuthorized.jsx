import React from "react";
import { Link } from "react-router-dom";

export default function NotAuthorized() {
  return (
    <div className="rounded-lg bg-white p-8 shadow-md dark:bg-gray-800">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">403</h1>
      <p className="mt-2 text-gray-600 dark:text-gray-400">
        You don&apos;t have permission to access this page.
      </p>
      <Link
        to="/"
        className="mt-6 inline-flex rounded-lg bg-orange-500 px-4 py-2 font-medium text-white hover:bg-orange-600"
      >
        Back to Dashboard
      </Link>
    </div>
  );
}

