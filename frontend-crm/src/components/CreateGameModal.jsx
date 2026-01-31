import React, { useState } from 'react';
import { gameAPI } from '../api/client';

const CreateGameModal = ({ isOpen, onClose, onSuccess }) => {
    const [formData, setFormData] = useState({
        name: '',
        provider: '',
        rtp: 96.0,
        status: 'active',
        image_url: '',
        description: '',
        min_bet: 0.1,
        max_bet: 100.0
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    if (!isOpen) return null;

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        try {
            const response = await gameAPI.create({
                ...formData,
                rtp: parseFloat(formData.rtp),
                min_bet: parseFloat(formData.min_bet),
                max_bet: parseFloat(formData.max_bet)
            });
            if (response.success) {
                onSuccess();
                onClose();
            } else {
                setError(response.error?.message || response.detail || 'Failed to create game');
            }
        } catch (err) {
            setError(err.response?.data?.error?.message || err.response?.data?.detail || err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center overflow-x-hidden overflow-y-auto outline-none focus:outline-none">
            <div className="fixed inset-0 bg-black opacity-50"></div>
            <div className="relative w-full max-w-lg mx-auto my-6 z-50">
                <div className="relative flex flex-col w-full bg-white dark:bg-gray-800 border-0 rounded-lg shadow-lg outline-none focus:outline-none">
                    <div className="flex items-center justify-between p-5 border-b border-solid border-gray-300 dark:border-gray-700 rounded-t">
                        <h3 className="text-xl font-semibold dark:text-white">Add New Machine</h3>
                        <button
                            className="p-1 ml-auto bg-transparent border-0 text-black dark:text-white float-right text-3xl leading-none font-semibold outline-none focus:outline-none"
                            onClick={onClose}
                        >
                            ×
                        </button>
                    </div>
                    <form onSubmit={handleSubmit}>
                        <div className="relative p-6 flex-auto grid grid-cols-2 gap-4">
                            {error && (
                                <div className="col-span-2 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
                                    {error}
                                </div>
                            )}
                            <div className="col-span-2">
                                <label className="block text-gray-700 dark:text-gray-300 text-sm font-bold mb-2">
                                    Game Name
                                </label>
                                <input
                                    type="text"
                                    required
                                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 dark:text-white dark:bg-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                                    value={formData.name}
                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                    placeholder="e.g. Mega Fortune"
                                />
                            </div>
                            <div className="col-span-1">
                                <label className="block text-gray-700 dark:text-gray-300 text-sm font-bold mb-2">
                                    Provider
                                </label>
                                <input
                                    type="text"
                                    required
                                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 dark:text-white dark:bg-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                                    value={formData.provider}
                                    onChange={(e) => setFormData({ ...formData, provider: e.target.value })}
                                    placeholder="e.g. NetEnt"
                                />
                            </div>
                            <div className="col-span-1">
                                <label className="block text-gray-700 dark:text-gray-300 text-sm font-bold mb-2">
                                    RTP (%)
                                </label>
                                <input
                                    type="number"
                                    step="0.1"
                                    required
                                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 dark:text-white dark:bg-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                                    value={formData.rtp}
                                    onChange={(e) => setFormData({ ...formData, rtp: e.target.value })}
                                />
                            </div>
                            <div className="col-span-1">
                                <label className="block text-gray-700 dark:text-gray-300 text-sm font-bold mb-2">
                                    Min Bet
                                </label>
                                <input
                                    type="number"
                                    step="0.1"
                                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 dark:text-white dark:bg-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                                    value={formData.min_bet}
                                    onChange={(e) => setFormData({ ...formData, min_bet: e.target.value })}
                                />
                            </div>
                            <div className="col-span-1">
                                <label className="block text-gray-700 dark:text-gray-300 text-sm font-bold mb-2">
                                    Max Bet
                                </label>
                                <input
                                    type="number"
                                    step="1"
                                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 dark:text-white dark:bg-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                                    value={formData.max_bet}
                                    onChange={(e) => setFormData({ ...formData, max_bet: e.target.value })}
                                />
                            </div>
                            <div className="col-span-2">
                                <label className="block text-gray-700 dark:text-gray-300 text-sm font-bold mb-2">
                                    Image URL
                                </label>
                                <input
                                    type="text"
                                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 dark:text-white dark:bg-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                                    value={formData.image_url}
                                    onChange={(e) => setFormData({ ...formData, image_url: e.target.value })}
                                    placeholder="https://..."
                                />
                            </div>
                            <div className="col-span-2">
                                <label className="block text-gray-700 dark:text-gray-300 text-sm font-bold mb-2">
                                    Description
                                </label>
                                <textarea
                                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 dark:text-white dark:bg-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                                    value={formData.description}
                                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                    rows="2"
                                ></textarea>
                            </div>
                        </div>
                        <div className="flex items-center justify-end p-6 border-t border-solid border-gray-300 dark:border-gray-700 rounded-b">
                            <button
                                className="text-gray-500 background-transparent font-bold uppercase px-6 py-2 text-sm outline-none focus:outline-none mr-1 mb-1 ease-linear transition-all duration-150"
                                type="button"
                                onClick={onClose}
                            >
                                Cancel
                            </button>
                            <button
                                className="bg-blue-600 hover:bg-blue-700 text-white active:bg-blue-800 font-bold uppercase text-sm px-6 py-3 rounded shadow hover:shadow-lg outline-none focus:outline-none mr-1 mb-1 ease-linear transition-all duration-150 disabled:opacity-50"
                                type="submit"
                                disabled={loading}
                            >
                                {loading ? 'Adding...' : 'Add Machine'}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default CreateGameModal;
