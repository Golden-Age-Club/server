import React, { useState, useEffect } from "react";
import { financeAPI } from "../api/client";
import ManualAdjustmentModal from "../components/ManualAdjustmentModal";

export default function FinancePage() {
    const [transactions, setTransactions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filters, setFilters] = useState({
        player_id: "",
        type: "",
        page: 1,
        page_size: 20
    });
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [activeTab, setActiveTab] = useState("history"); // "history" or "approvals"
    const [pendingApprovals, setPendingApprovals] = useState([]);

    const fetchTransactions = async () => {
        setLoading(true);
        try {
            const response = await financeAPI.list(filters);
            if (response.success) {
                setTransactions(response.data || []);
            }
        } catch (err) {
            console.error("Failed to fetch transactions:", err);
        } finally {
            setLoading(false);
        }
    };

    const fetchPendingApprovals = async () => {
        setLoading(true);
        try {
            const response = await financeAPI.getPendingApprovals();
            if (response.success) {
                setPendingApprovals(response.data || []);
            }
        } catch (err) {
            console.error("Failed to fetch pending approvals:", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (activeTab === "history") {
            fetchTransactions();
        } else {
            fetchPendingApprovals();
        }
    }, [filters, activeTab]);

    const handleApprove = async (txId) => {
        if (!window.confirm("Are you sure you want to APPROVE this transaction? This will update the player's balance.")) return;
        try {
            const response = await financeAPI.approveTransaction(txId);
            if (response.success) {
                alert("Transaction approved successfully");
                fetchPendingApprovals();
            }
        } catch (err) {
            alert(err.message || "Failed to approve");
        }
    };

    const handleReject = async (txId) => {
        if (!window.confirm("Are you sure you want to REJECT this transaction?")) return;
        try {
            const response = await financeAPI.rejectTransaction(txId);
            if (response.success) {
                alert("Transaction rejected");
                fetchPendingApprovals();
            }
        } catch (err) {
            alert(err.message || "Failed to reject");
        }
    };

    const getStatusColor = (status) => {
        switch (status) {
            case "completed": return "bg-green-100 text-green-800";
            case "pending": return "bg-yellow-100 text-yellow-800 border border-yellow-200";
            case "failed": return "bg-red-100 text-red-800";
            default: return "bg-gray-100 text-gray-800";
        }
    };

    const getTypeColor = (type) => {
        switch (type) {
            case "deposit": return "text-green-600";
            case "withdrawal": return "text-red-600";
            case "bet": return "text-blue-600";
            case "win": return "text-purple-600";
            case "adjustment": return "text-orange-600";
            default: return "text-gray-600";
        }
    };

    return (
        <div className="p-4 md:p-6">
            <div className="mb-6 flex flex-col md:flex-row md:items-center md:justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Finance & Transactions</h1>
                    <p className="mt-1 text-gray-600 dark:text-gray-400">Monitor all financial movements and manage approvals.</p>
                </div>
                <button
                    onClick={() => setIsModalOpen(true)}
                    className="mt-4 md:mt-0 inline-flex items-center justify-center rounded-md bg-primary py-2 px-6 text-white hover:bg-opacity-90 font-semibold shadow-sm transition-all"
                >
                    Manual Adjustment
                </button>
            </div>

            {/* Tabs */}
            <div className="mb-6 flex border-b border-gray-200 dark:border-gray-700">
                <button
                    className={`py-2 px-4 font-medium text-sm transition-colors ${activeTab === 'history' ? 'border-b-2 border-primary text-primary' : 'text-gray-500 hover:text-gray-700 dark:text-gray-400'}`}
                    onClick={() => setActiveTab('history')}
                >
                    Transaction History
                </button>
                <button
                    className={`py-2 px-4 font-medium text-sm transition-colors relative ${activeTab === 'approvals' ? 'border-b-2 border-primary text-primary' : 'text-gray-500 hover:text-gray-700 dark:text-gray-400'}`}
                    onClick={() => setActiveTab('approvals')}
                >
                    Pending Approvals
                    {pendingApprovals.length > 0 && (
                        <span className="ml-2 inline-flex items-center justify-center px-2 py-0.5 text-xs font-bold leading-none text-white bg-red-500 rounded-full">
                            {pendingApprovals.length}
                        </span>
                    )}
                </button>
            </div>

            {activeTab === 'history' ? (
                <>
                    <div className="mb-6 grid grid-cols-1 gap-4 md:grid-cols-4">
                        <input
                            type="text"
                            placeholder="Filter by Player ID"
                            className="rounded border border-gray-300 p-2 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                            value={filters.player_id}
                            onChange={(e) => setFilters({ ...filters, player_id: e.target.value, page: 1 })}
                        />
                        <select
                            className="rounded border border-gray-300 p-2 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                            value={filters.type}
                            onChange={(e) => setFilters({ ...filters, type: e.target.value, page: 1 })}
                        >
                            <option value="">All Types</option>
                            <option value="deposit">Deposit</option>
                            <option value="withdrawal">Withdrawal</option>
                            <option value="bet">Bet</option>
                            <option value="win">Win</option>
                            <option value="adjustment">Adjustment</option>
                            <option value="bonus">Bonus</option>
                        </select>
                    </div>

                    <div className="overflow-x-auto rounded-lg bg-white shadow-md dark:bg-gray-800">
                        <table className="w-full text-left text-sm text-gray-500 dark:text-gray-400">
                            <thead className="bg-gray-50 text-xs uppercase text-gray-700 dark:bg-gray-700 dark:text-gray-400">
                                <tr>
                                    <th className="px-6 py-3">Transaction ID</th>
                                    <th className="px-6 py-3">Player ID</th>
                                    <th className="px-6 py-3">Type</th>
                                    <th className="px-6 py-3">Amount</th>
                                    <th className="px-6 py-3">Balance (Bef/Aft)</th>
                                    <th className="px-6 py-3">Status</th>
                                    <th className="px-6 py-3">Date</th>
                                    <th className="px-6 py-3">By</th>
                                </tr>
                            </thead>
                            <tbody>
                                {loading ? (
                                    <tr>
                                        <td colSpan="8" className="px-6 py-10 text-center">Loading transactions...</td>
                                    </tr>
                                ) : transactions.length === 0 ? (
                                    <tr>
                                        <td colSpan="8" className="px-6 py-10 text-center">No transactions found.</td>
                                    </tr>
                                ) : (
                                    transactions.map((tx) => (
                                        <tr key={tx.transaction_id} className="border-b bg-white hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:hover:bg-gray-600">
                                            <td className="px-6 py-4 font-mono text-xs">{tx.transaction_id}</td>
                                            <td className="px-6 py-4">{tx.player_id}</td>
                                            <td className="px-6 py-4">
                                                <span className={`font-medium ${getTypeColor(tx.type)}`}>
                                                    {tx.type.toUpperCase()}
                                                </span>
                                            </td>
                                            <td className={`px-6 py-4 font-bold ${tx.amount >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                                {tx.amount >= 0 ? '+' : ''}{tx.amount.toFixed(2)}
                                            </td>
                                            <td className="px-6 py-4 text-xs">
                                                {tx.amount_before.toFixed(2)} → {tx.amount_after.toFixed(2)}
                                            </td>
                                            <td className="px-6 py-4">
                                                <span className={`rounded-full px-2 py-1 text-xs font-semibold ${getStatusColor(tx.status)}`}>
                                                    {tx.status}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 text-xs">
                                                {new Date(tx.created_at).toLocaleString('en-GB', {
                                                    day: '2-digit', month: '2-digit', year: 'numeric',
                                                    hour: '2-digit', minute: '2-digit'
                                                })}
                                            </td>
                                            <td className="px-6 py-4 text-xs italic">{tx.created_by?.split('_')[1] || tx.created_by}</td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                </>
            ) : (
                /* Approvals View */
                <div className="overflow-x-auto rounded-lg bg-white shadow-md dark:bg-gray-800">
                    <table className="w-full text-left text-sm text-gray-500 dark:text-gray-400">
                        <thead className="bg-gray-50 text-xs uppercase text-gray-700 dark:bg-gray-700 dark:text-gray-400">
                            <tr>
                                <th className="px-6 py-3">Player ID</th>
                                <th className="px-6 py-3">Type</th>
                                <th className="px-6 py-3">Amount</th>
                                <th className="px-6 py-3">Date</th>
                                <th className="px-6 py-3">Creator</th>
                                <th className="px-6 py-3">Remarks</th>
                                <th className="px-6 py-3 text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {loading ? (
                                <tr>
                                    <td colSpan="7" className="px-6 py-10 text-center">Loading approvals...</td>
                                </tr>
                            ) : pendingApprovals.length === 0 ? (
                                <tr>
                                    <td colSpan="7" className="px-6 py-10 text-center">All caught up! No pending approvals.</td>
                                </tr>
                            ) : (
                                pendingApprovals.map((tx) => (
                                    <tr key={tx.transaction_id} className="border-b bg-white hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:hover:bg-gray-600">
                                        <td className="px-6 py-4 font-bold">{tx.player_id}</td>
                                        <td className="px-6 py-4">
                                            <span className={`font-medium ${getTypeColor(tx.type)}`}>
                                                {tx.type.toUpperCase()}
                                            </span>
                                        </td>
                                        <td className={`px-6 py-4 font-bold ${tx.amount >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                            {tx.amount >= 0 ? '+' : ''}{tx.amount.toFixed(2)}
                                        </td>
                                        <td className="px-6 py-4 text-xs">
                                            {new Date(tx.created_at).toLocaleString()}
                                        </td>
                                        <td className="px-6 py-4 text-xs italic">{tx.created_by?.split('_')[1] || tx.created_by}</td>
                                        <td className="px-6 py-4 max-w-xs truncate">{tx.remarks}</td>
                                        <td className="px-6 py-4 text-right">
                                            <div className="flex justify-end gap-2">
                                                <button
                                                    onClick={() => handleApprove(tx.transaction_id)}
                                                    className="rounded bg-green-500 px-3 py-1 text-xs font-semibold text-white hover:bg-green-600 transition-colors"
                                                >
                                                    Approve
                                                </button>
                                                <button
                                                    onClick={() => handleReject(tx.transaction_id)}
                                                    className="rounded bg-red-500 px-3 py-1 text-xs font-semibold text-white hover:bg-red-600 transition-colors"
                                                >
                                                    Reject
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            )}

            <ManualAdjustmentModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onSuccess={() => {
                    if (activeTab === 'history') fetchTransactions();
                    else fetchPendingApprovals();
                }}
            />
        </div>
    );
}
