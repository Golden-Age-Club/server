import React, { useState, useEffect } from "react";
import { gameAPI } from "../api/client";
import { Search, Plus, Filter, Gamepad2, Settings, Ban, CheckCircle } from "lucide-react";
import CreateGameModal from "../components/CreateGameModal";

export default function GamesPage() {
    const [games, setGames] = useState([]);
    const [loading, setLoading] = useState(false);
    const [search, setSearch] = useState("");
    const [statusFilter, setStatusFilter] = useState("");
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [isModalOpen, setIsModalOpen] = useState(false);

    const fetchGames = async () => {
        try {
            setLoading(true);
            const data = await gameAPI.list({
                page,
                page_size: 12,
                search: search || undefined,
                status: statusFilter || undefined,
            });
            setGames(data.data || []);
            setTotalPages(data.total_pages || 1);
        } catch (err) {
            console.error("Failed to load games", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        const timer = setTimeout(() => {
            fetchGames();
        }, 300);
        return () => clearTimeout(timer);
    }, [page, search, statusFilter]);

    const handleToggleStatus = async (game) => {
        try {
            const newStatus = game.status === 'active' ? 'inactive' : 'active';
            await gameAPI.update(game.game_id, { status: newStatus });
            fetchGames();
        } catch (err) {
            alert("Failed to update status");
        }
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Machine Management</h1>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Manage arcade machines and games</p>
                </div>
                <button
                    onClick={() => setIsModalOpen(true)}
                    className="inline-flex items-center justify-center rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-4 focus:ring-blue-300 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800"
                >
                    <Plus className="mr-2 h-4 w-4" />
                    Add Machine
                </button>
            </div>

            {/* Filters */}
            <div className="flex flex-col gap-4 rounded-lg border border-gray-200 bg-white p-4 shadow-sm dark:border-gray-700 dark:bg-gray-800 sm:flex-row">
                <div className="relative flex-1">
                    <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                        <Search className="h-5 w-5 text-gray-400" />
                    </div>
                    <input
                        type="text"
                        placeholder="Search games or providers..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 pl-10 text-sm text-gray-900 focus:border-blue-500 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:placeholder-gray-400 dark:focus:border-blue-500 dark:focus:ring-blue-500"
                    />
                </div>
                <div className="flex gap-4">
                    <select
                        value={statusFilter}
                        onChange={(e) => setStatusFilter(e.target.value)}
                        className="block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-blue-500 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:placeholder-gray-400 dark:focus:border-blue-500 dark:focus:ring-blue-500"
                    >
                        <option value="">All Status</option>
                        <option value="active">Active</option>
                        <option value="inactive">Inactive</option>
                        <option value="maintenance">Maintenance</option>
                    </select>
                </div>
            </div>

            {/* Grid */}
            {loading ? (
                <div className="flex h-64 items-center justify-center">
                    <div className="h-8 w-8 animate-spin rounded-full border-4 border-gray-200 border-t-blue-600"></div>
                </div>
            ) : (
                <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                    {games.length === 0 ? (
                        <div className="col-span-full flex h-64 flex-col items-center justify-center rounded-lg border-2 border-dashed border-gray-300 bg-gray-50 dark:border-gray-700 dark:bg-gray-800">
                            <Gamepad2 className="mb-4 h-12 w-12 text-gray-400" />
                            <p className="text-gray-500 dark:text-gray-400">No games found</p>
                        </div>
                    ) : (
                        games.map((game) => (
                            <div key={game.game_id} className="overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm dark:border-gray-700 dark:bg-gray-800">
                                <div className="relative h-40 bg-gray-200 dark:bg-gray-700">
                                    {game.image_url ? (
                                        <img src={game.image_url} alt={game.name} className="h-full w-full object-cover" />
                                    ) : (
                                        <div className="flex h-full items-center justify-center">
                                            <Gamepad2 className="h-12 w-12 text-gray-400" />
                                        </div>
                                    )}
                                    <div className="absolute right-2 top-2">
                                        <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${game.status === 'active'
                                            ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'
                                            : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
                                            }`}>
                                            {game.status}
                                        </span>
                                    </div>
                                </div>

                                <div className="p-4">
                                    <h3 className="text-lg font-bold text-gray-900 dark:text-white">{game.name}</h3>
                                    <p className="text-sm text-gray-500 dark:text-gray-400">{game.provider}</p>

                                    <div className="mt-4 flex items-center justify-between">
                                        <span className="text-xs font-medium text-gray-500 dark:text-gray-400">RTP: {game.rtp}%</span>
                                        <button
                                            onClick={() => handleToggleStatus(game)}
                                            className={`rounded p-1 sm:p-2 ${game.status === 'active'
                                                ? 'text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900/20'
                                                : 'text-green-600 hover:bg-green-50 dark:text-green-400 dark:hover:bg-green-900/20'
                                                }`}
                                        >
                                            {game.status === 'active' ? <Ban className="h-5 w-5" /> : <CheckCircle className="h-5 w-5" />}
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            )}

            <CreateGameModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onSuccess={fetchGames}
            />
        </div>
    );
}
