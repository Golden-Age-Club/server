import React, { useState } from 'react';
import { vipAPI } from '../api/client';

const VIPAdjustmentModal = ({ isOpen, onClose, onSuccess }) => {
    const [formData, setFormData] = useState({
        player_id: '',
        new_level: 0,
        reason: ''
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    if (!isOpen) return null;

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        try {
            const response = await vipAPI.adjustPlayerVIP({
                ...formData,
                new_level: parseInt(formData.new_level)
            });
            if (response.success) {
                onSuccess();
                onClose();
            } else {
                setError(response.error?.message || 'Adjustment failed');
            }
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center overflow-x-hidden overflow-y-auto outline-none focus:outline-none">
            <div className="fixed inset-0 bg-black opacity-50"></div>
            <div className="relative w-full max-w-md mx-auto my-6 z-50">
                <div className="relative flex flex-col w-full bg-white dark:bg-gray-800 border-0 rounded-lg shadow-lg outline-none focus:outline-none">
                    <div className="flex items-center justify-between p-5 border-b border-solid border-gray-300 dark:border-gray-700 rounded-t">
                        <h3 className="text-xl font-semibold dark:text-white">Manual VIP Adjustment</h3>
                        <button
                            className="p-1 ml-auto bg-transparent border-0 text-black dark:text-white float-right text-3xl leading-none font-semibold outline-none focus:outline-none"
                            onClick={onClose}
                        >
                            ×
                        </button>
                    </div>
                    <form onSubmit={handleSubmit}>
                        <div className="relative p-6 flex-auto">
                            {error && (
                                <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
                                    {error}
                                </div>
                            )}
                            <div className="mb-4">
                                <label className="block text-gray-700 dark:text-gray-300 text-sm font-bold mb-2">
                                    Player ID
                                </label>
                                <input
                                    type="text"
                                    required
                                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 dark:text-white dark:bg-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                                    value={formData.player_id}
                                    onChange={(e) => setFormData({ ...formData, player_id: e.target.value })}
                                />
                            </div>
                            <div className="mb-4">
                                <label className="block text-gray-700 dark:text-gray-300 text-sm font-bold mb-2">
                                    New VIP Level
                                </label>
                                <select
                                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 dark:text-white dark:bg-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                                    value={formData.new_level}
                                    onChange={(e) => setFormData({ ...formData, new_level: e.target.value })}
                                >
                                    <option value="0">Bronze (Level 0)</option>
                                    <option value="1">Silver (Level 1)</option>
                                    <option value="2">Gold (Level 2)</option>
                                    <option value="3">Platinum (Level 3)</option>
                                </select>
                            </div>
                            <div className="mb-4">
                                <label className="block text-gray-700 dark:text-gray-300 text-sm font-bold mb-2">
                                    Reason
                                </label>
                                <textarea
                                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 dark:text-white dark:bg-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                                    value={formData.reason}
                                    onChange={(e) => setFormData({ ...formData, reason: e.target.value })}
                                    rows="3"
                                    required
                                ></textarea>
                            </div>
                        </div>
                        <div className="flex items-center justify-end p-6 border-t border-solid border-gray-300 dark:border-gray-700 rounded-b">
                            <button
                                className="text-gray-500 background-transparent font-bold uppercase px-6 py-2 text-sm outline-none focus:outline-none mr-1 mb-1"
                                type="button"
                                onClick={onClose}
                            >
                                Cancel
                            </button>
                            <button
                                className="bg-primary hover:bg-opacity-90 text-white font-bold uppercase text-sm px-6 py-3 rounded shadow outline-none focus:outline-none mr-1 mb-1 disabled:opacity-50"
                                type="submit"
                                disabled={loading}
                            >
                                {loading ? 'Processing...' : 'Apply Change'}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default VIPAdjustmentModal;
