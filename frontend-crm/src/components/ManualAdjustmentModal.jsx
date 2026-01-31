import React, { useState } from 'react';
import { financeAPI } from '../api/client';

const ManualAdjustmentModal = ({ isOpen, onClose, onSuccess }) => {
    const [formData, setFormData] = useState({
        player_id: '',
        amount: '',
        type: 'adjustment',
        remarks: ''
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    if (!isOpen) return null;

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        try {
            let response;
            if (formData.type === 'withdrawal') {
                response = await financeAPI.requestWithdrawal({
                    ...formData,
                    amount: parseFloat(formData.amount)
                });
            } else {
                response = await financeAPI.adjust({
                    ...formData,
                    amount: parseFloat(formData.amount)
                });
            }
            if (response.success) {
                onSuccess();
                onClose();
            } else {
                setError(response.error?.message || response.detail || 'Adjustment failed');
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
            <div className="relative w-full max-w-md mx-auto my-6 z-50">
                <div className="relative flex flex-col w-full bg-white dark:bg-gray-800 border-0 rounded-lg shadow-lg outline-none focus:outline-none">
                    <div className="flex items-center justify-between p-5 border-b border-solid border-gray-300 dark:border-gray-700 rounded-t">
                        <h3 className="text-xl font-semibold dark:text-white">Manual Balance Adjustment</h3>
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
                                    placeholder="e.g. user_12345"
                                />
                            </div>
                            <div className="mb-4">
                                <label className="block text-gray-700 dark:text-gray-300 text-sm font-bold mb-2">
                                    Amount
                                </label>
                                <input
                                    type="number"
                                    step="0.01"
                                    required
                                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 dark:text-white dark:bg-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                                    value={formData.amount}
                                    onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                                    placeholder="Positive to add, negative to subtract"
                                />
                            </div>
                            <div className="mb-4">
                                <label className="block text-gray-700 dark:text-gray-300 text-sm font-bold mb-2">
                                    Type
                                </label>
                                <select
                                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 dark:text-white dark:bg-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                                    value={formData.type}
                                    onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                                >
                                    <option value="adjustment">Adjustment</option>
                                    <option value="bonus">Bonus</option>
                                    <option value="deposit">Manual Deposit</option>
                                    <option value="withdrawal">Manual Withdrawal</option>
                                </select>
                            </div>
                            <div className="mb-4">
                                <label className="block text-gray-700 dark:text-gray-300 text-sm font-bold mb-2">
                                    Remarks
                                </label>
                                <textarea
                                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 dark:text-white dark:bg-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                                    value={formData.remarks}
                                    onChange={(e) => setFormData({ ...formData, remarks: e.target.value })}
                                    placeholder="Reason for adjustment"
                                    rows="3"
                                    required
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
                                className="bg-primary hover:bg-opacity-90 text-white active:bg-primary font-bold uppercase text-sm px-6 py-3 rounded shadow hover:shadow-lg outline-none focus:outline-none mr-1 mb-1 ease-linear transition-all duration-150 disabled:opacity-50"
                                type="submit"
                                disabled={loading}
                            >
                                {loading ? 'Processing...' : 'Submit Adjustment'}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default ManualAdjustmentModal;
