import React, { useState, useEffect } from "react";
import { vipAPI } from "../api/client";
import VIPAdjustmentModal from "../components/VIPAdjustmentModal";

export default function VIPPage() {
    const [configs, setConfigs] = useState([]);
    const [highValuePlayers, setHighValuePlayers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [editingConfigs, setEditingConfigs] = useState(false);
    const [isAdjustModalOpen, setIsAdjustModalOpen] = useState(false);

    const fetchData = async () => {
        setLoading(true);
        try {
            const [configRes, hvRes] = await Promise.all([
                vipAPI.getConfigs(),
                vipAPI.getHighValuePlayers()
            ]);

            if (configRes.success && Array.isArray(configRes.data)) {
                setConfigs(configRes.data);
            }
            if (hvRes.success && Array.isArray(hvRes.data)) {
                setHighValuePlayers(hvRes.data);
            }
        } catch (err) {
            console.error("Failed to fetch VIP data:", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const handleConfigChange = (index, field, value) => {
        const newConfigs = [...configs];
        newConfigs[index][field] = value;
        setConfigs(newConfigs);
    };

    const handleSaveConfigs = async () => {
        setLoading(true);
        try {
            const response = await vipAPI.updateConfigs(configs);
            if (response.success) {
                setEditingConfigs(false);
                fetchData();
            }
        } catch (err) {
            alert("Failed to save configs: " + err.message);
        } finally {
            setLoading(false);
        }
    };

    const getTierBadge = (level) => {
        const badges = {
            0: "bg-orange-100 text-orange-800",
            1: "bg-gray-100 text-gray-800",
            2: "bg-yellow-100 text-yellow-800",
            3: "bg-purple-100 text-purple-800"
        };
        return badges[level] || "bg-blue-100 text-blue-800";
    };

    return (
        <div className="p-4 md:p-6">
            <div className="mb-6 flex flex-col md:flex-row md:items-center md:justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 dark:text-white">VIP & Segmentation</h1>
                    <p className="mt-1 text-gray-600 dark:text-gray-400">Configure VIP tiers and manage high-value users.</p>
                </div>
                <button
                    onClick={() => setIsAdjustModalOpen(true)}
                    className="mt-4 md:mt-0 inline-flex items-center justify-center rounded-md bg-primary py-2 px-6 text-white hover:bg-opacity-90 font-semibold"
                >
                    Manual VIP Promotion
                </button>
            </div>

            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
                {/* VIP Tiers Configuration */}
                <div className="rounded-lg bg-white p-6 shadow-md dark:bg-gray-800">
                    <div className="mb-4 flex items-center justify-between">
                        <h2 className="text-xl font-bold dark:text-white">Tier Configurations</h2>
                        {!editingConfigs ? (
                            <button
                                onClick={() => setEditingConfigs(true)}
                                className="text-primary hover:underline text-sm font-medium"
                            >
                                Edit Tiers
                            </button>
                        ) : (
                            <div className="space-x-4">
                                <button
                                    onClick={() => setEditingConfigs(false)}
                                    className="text-gray-500 hover:text-gray-700 text-sm font-medium"
                                >
                                    Cancel
                                </button>
                                <button
                                    onClick={handleSaveConfigs}
                                    className="bg-primary text-white px-3 py-1 rounded text-sm font-medium"
                                >
                                    Save Changes
                                </button>
                            </div>
                        )}
                    </div>

                    <div className="space-y-4">
                        {configs.map((tier, idx) => (
                            <div key={idx} className="border-b dark:border-gray-700 pb-4 last:border-0">
                                <div className="flex items-center justify-between mb-2">
                                    <span className={`rounded px-2 py-0.5 text-xs font-bold uppercase ${getTierBadge(tier.level)}`}>
                                        {tier.name} (Lvl {tier.level})
                                    </span>
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-xs text-gray-500 mb-1">Min Deposits</label>
                                        <input
                                            type="number"
                                            disabled={!editingConfigs}
                                            className="w-full rounded border p-1 text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white disabled:opacity-50"
                                            value={tier.min_deposits}
                                            onChange={(e) => handleConfigChange(idx, 'min_deposits', parseFloat(e.target.value))}
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-xs text-gray-500 mb-1">Min Bets</label>
                                        <input
                                            type="number"
                                            disabled={!editingConfigs}
                                            className="w-full rounded border p-1 text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white disabled:opacity-50"
                                            value={tier.min_bet_amount}
                                            onChange={(e) => handleConfigChange(idx, 'min_bet_amount', parseFloat(e.target.value))}
                                        />
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* High Value Players */}
                <div className="rounded-lg bg-white p-6 shadow-md dark:bg-gray-800">
                    <h2 className="mb-4 text-xl font-bold dark:text-white">High-Value Users</h2>
                    <div className="overflow-x-auto">
                        <table className="w-full text-left text-sm text-gray-500 dark:text-gray-400">
                            <thead className="bg-gray-50 text-xs uppercase text-gray-700 dark:bg-gray-700 dark:text-gray-400">
                                <tr>
                                    <th className="px-4 py-3">Player</th>
                                    <th className="px-4 py-3">Level</th>
                                    <th className="px-4 py-3">Total Dep.</th>
                                    <th className="px-4 py-3">Balance</th>
                                </tr>
                            </thead>
                            <tbody>
                                {loading ? (
                                    <tr><td colSpan="4" className="py-10 text-center">Loading players...</td></tr>
                                ) : highValuePlayers.length === 0 ? (
                                    <tr><td colSpan="4" className="py-10 text-center">No high-value players found.</td></tr>
                                ) : (
                                    highValuePlayers.map(player => (
                                        <tr key={player.player_id} className="border-b dark:border-gray-700">
                                            <td className="px-4 py-3">
                                                <div className="font-medium text-gray-900 dark:text-white">{player.username}</div>
                                                <div className="text-xs">{player.player_id}</div>
                                            </td>
                                            <td className="px-4 py-3">
                                                <span className={`rounded-full px-2 py-0.5 text-xs font-semibold ${getTierBadge(player.vip_level)}`}>
                                                    Level {player.vip_level}
                                                </span>
                                            </td>
                                            <td className="px-4 py-3 font-mono">${(player.total_deposits || 0).toLocaleString()}</td>
                                            <td className="px-4 py-3 font-mono text-green-600">${(player.balance || 0).toLocaleString()}</td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <VIPAdjustmentModal
                isOpen={isAdjustModalOpen}
                onClose={() => setIsAdjustModalOpen(false)}
                onSuccess={fetchData}
            />
        </div>
    );
}
