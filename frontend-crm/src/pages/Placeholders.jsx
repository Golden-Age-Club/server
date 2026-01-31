import React from "react";

function PlaceholderPage({ title, description }) {
  return (
    <div className="rounded-lg bg-white p-8 shadow-md dark:bg-gray-800">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{title}</h1>
      <p className="mt-2 text-gray-600 dark:text-gray-400">
        {description ?? "This module is scaffolded and ready for API integration."}
      </p>
    </div>
  );
}

export function UsersPage() {
  return <PlaceholderPage title="User Management" description="Search/filter users, view VIP/risk, freeze/unfreeze." />;
}

export function FinancePage() {
  return <PlaceholderPage title="Wallet & Finance" description="Balances, deposits, withdrawal approvals, manual adjustments (double confirm)." />;
}

export function BetsPage() {
  return <PlaceholderPage title="Bets & Games" description="Bet records, round details, enable/disable games." />;
}

export function ReportsPage() {
  return <PlaceholderPage title="Reports & Dashboard" description="Core metrics (GGR/RTP/DAU) and export (CSV/Excel)." />;
}

export function SystemPage() {
  return <PlaceholderPage title="System & Logs" description="Platform parameters, admin accounts, operation logs/audit." />;
}

