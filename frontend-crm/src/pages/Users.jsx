import React, { useState, useEffect } from "react";
import { playerAPI } from "../api/client";
import CreateUserModal from "../components/CreateUserModal";
import EditUserModal from "../components/EditUserModal";

export default function UsersPage() {
    const [players, setPlayers] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    // Modal state
    const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
    const [isEditModalOpen, setIsEditModalOpen] = useState(false);
    const [selectedPlayer, setSelectedPlayer] = useState(null);

    // Filters
    const [search, setSearch] = useState("");
    const [statusFilter, setStatusFilter] = useState("");
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);

    const fetchPlayers = async () => {
        try {
            setLoading(true);
            const data = await playerAPI.list({
                page,
                page_size: 10,
                search: search || undefined,
                status: statusFilter || undefined,
            });

            setPlayers(data.data || []);
            setTotalPages(data.total_pages || 1);
            setError(null);
        } catch (err) {
            console.error("Failed to fetch players", err);
            setError("Failed to load users");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        const timer = setTimeout(() => {
            fetchPlayers();
        }, 300); // Debounce search
        return () => clearTimeout(timer);
    }, [page, search, statusFilter]);

    const handleStatusChange = (e) => {
        setStatusFilter(e.target.value);
        setPage(1);
    };

    const handleSearchChange = (e) => {
        setSearch(e.target.value);
        setPage(1);
    };

    const handleSuccess = () => {
        fetchPlayers();
    };

    const openEditModal = (player) => {
        setSelectedPlayer(player);
        setIsEditModalOpen(true);
    };

    const handleBlockUser = async (player) => {
        if (!window.confirm(`Are you sure you want to block ${player.username}?`)) return;
        try {
            await playerAPI.update(player.player_id, { status: 'banned' });
            fetchPlayers();
        } catch (err) {
            const errorMessage = err.response?.data?.error?.message ||
                err.response?.data?.detail ||
                err.message ||
                "Failed to block user";
            alert("Failed to block user: " + errorMessage);
        }
    };

    return (
        <div className="space-y-6">
            <CreateUserModal
                isOpen={isCreateModalOpen}
                onClose={() => setIsCreateModalOpen(false)}
                onSuccess={handleSuccess}
            />

            <EditUserModal
                isOpen={isEditModalOpen}
                onClose={() => setIsEditModalOpen(false)}
                onSuccess={handleSuccess}
                player={selectedPlayer}
            />

            {/* Header */}
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Player Management</h1>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Manage registered players and VIP status</p>
                </div>
                <button
                    onClick={() => setIsCreateModalOpen(true)}
                    className="inline-flex items-center justify-center rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-4 focus:ring-blue-300 dark:focus:ring-blue-800"
                >
                    Add New Player
                </button>
            </div>

            {/* Filters */}
            <div className="flex flex-col gap-4 bg-white p-4 shadow dark:bg-gray-800 sm:flex-row sm:rounded-lg">
                <div className="flex-1">
                    <input
                        type="text"
                        placeholder="Search by username, email, ID..."
                        value={search}
                        onChange={handleSearchChange}
                        className="block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-blue-500 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:placeholder-gray-400"
                    />
                </div>
                <div>
                    <select
                        value={statusFilter}
                        onChange={handleStatusChange}
                        className="block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-blue-500 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                    >
                        <option value="">All Status</option>
                        <option value="active">Active</option>
                        <option value="suspended">Suspended</option>
                        <option value="frozen">Frozen</option>
                        <option value="banned">Banned</option>
                    </select>
                </div>
            </div>

            {/* Table */}
            <div className="relative overflow-x-auto shadow-md sm:rounded-lg">
                <table className="w-full text-left text-sm text-gray-500 dark:text-gray-400">
                    <thead className="bg-gray-50 text-xs uppercase text-gray-700 dark:bg-gray-700 dark:text-gray-400">
                        <tr>
                            <th scope="col" className="px-6 py-3">Player</th>
                            <th scope="col" className="px-6 py-3">Status</th>
                            <th scope="col" className="px-6 py-3">VIP Level</th>
                            <th scope="col" className="px-6 py-3">Balance</th>
                            <th scope="col" className="px-6 py-3">Joined</th>
                            <th scope="col" className="px-6 py-3">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {loading ? (
                            <tr>
                                <td colSpan="6" className="px-6 py-4 text-center">Loading players...</td>
                            </tr>
                        ) : error ? (
                            <tr>
                                <td colSpan="6" className="px-6 py-4 text-center text-red-500">{error}</td>
                            </tr>
                        ) : players.length === 0 ? (
                            <tr>
                                <td colSpan="6" className="px-6 py-4 text-center">No players found</td>
                            </tr>
                        ) : (
                            players.map((player) => (
                                <tr key={player.player_id} className="border-b bg-white hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:hover:bg-gray-600">
                                    <td className="px-6 py-4">
                                        <div className="flex items-center">
                                            <div className="h-10 w-10 flex-shrink-0 rounded-full bg-gray-200 dark:bg-gray-600 flex items-center justify-center text-lg font-bold uppercase text-gray-500 dark:text-gray-300">
                                                {player.username.substring(0, 2)}
                                            </div>
                                            <div className="ml-4">
                                                <div className="font-medium text-gray-900 dark:text-white">{player.username}</div>
                                                <div className="text-xs text-gray-500">{player.email || "No email"}</div>
                                                <div className="text-xs text-gray-400 font-mono">{player.player_id}</div>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <span className={`rounded px-2.5 py-0.5 text-xs font-medium ${player.status === 'active' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300' :
                                            player.status === 'suspended' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300' :
                                                'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
                                            }`}>
                                            {player.status.toUpperCase()}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="flex items-center">
                                            <span className="text-yellow-500 mr-1">👑</span>
                                            <span className="font-semibold">{player.vip_level}</span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 font-mono font-medium text-gray-900 dark:text-white">
                                        ${player.balance.toFixed(2)}
                                    </td>
                                    <td className="px-6 py-4">
                                        {new Date(player.created_at).toLocaleDateString()}
                                    </td>
                                    <td className="px-6 py-4">
                                        <button
                                            onClick={() => openEditModal(player)}
                                            className="font-medium text-blue-600 hover:underline dark:text-blue-500 mr-3"
                                        >
                                            Edit
                                        </button>
                                        <button
                                            onClick={() => handleBlockUser(player)}
                                            className="font-medium text-red-600 hover:underline dark:text-red-500"
                                        >
                                            Block
                                        </button>
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>

            {/* Pagination */}
            <div className="flex justify-center">
                <nav aria-label="Page navigation">
                    <ul className="inline-flex items-center -space-x-px">
                        <li>
                            <button
                                onClick={() => setPage(p => Math.max(1, p - 1))}
                                disabled={page === 1}
                                className="ml-0 block rounded-l-lg border border-gray-300 bg-white px-3 py-2 leading-tight text-gray-500 hover:bg-gray-100 hover:text-gray-700 disabled:opacity-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-white"
                            >
                                Previous
                            </button>
                        </li>
                        {[...Array(totalPages)].map((_, i) => (
                            <li key={i}>
                                <button
                                    onClick={() => setPage(i + 1)}
                                    className={`block border border-gray-300 px-3 py-2 leading-tight ${page === i + 1
                                        ? "bg-blue-50 text-blue-600 hover:bg-blue-100 hover:text-blue-700 dark:border-gray-700 dark:bg-gray-700 dark:text-white"
                                        : "bg-white text-gray-500 hover:bg-gray-100 hover:text-gray-700 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-white"
                                        }`}
                                >
                                    {i + 1}
                                </button>
                            </li>
                        ))}
                        <li>
                            <button
                                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                                disabled={page === totalPages}
                                className="block rounded-r-lg border border-gray-300 bg-white px-3 py-2 leading-tight text-gray-500 hover:bg-gray-100 hover:text-gray-700 disabled:opacity-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-white"
                            >
                                Next
                            </button>
                        </li>
                    </ul>
                </nav>
            </div>
        </div>
    );
}
