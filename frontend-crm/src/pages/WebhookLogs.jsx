import React, { useState, useEffect } from 'react';
import { Database, RefreshCw, Trash2 } from 'lucide-react';
import { auditAPI } from '../api/client';
import { toast } from 'react-hot-toast';

// Modal to view raw payload
const PayloadModal = ({ isOpen, onClose, data }) => {
    if (!isOpen) return null;
    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 transition-opacity duration-300">
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-2xl max-h-[85vh] flex flex-col border border-gray-100 dark:border-gray-700 animate-in fade-in zoom-in duration-200">
                <div className="flex justify-between items-center p-5 border-b border-gray-100 dark:border-gray-700">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-blue-50 dark:bg-blue-900/30 text-blue-600 rounded-lg">
                            <Database className="w-5 h-5" />
                        </div>
                        <h3 className="text-xl font-bold text-gray-800 dark:text-white">Webhook Payload</h3>
                    </div>
                    <button onClick={onClose} className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors">
                        <RefreshCw className="h-6 w-6" />
                    </button>
                </div>
                <div className="p-5 overflow-y-auto flex-1 bg-gray-50/50 dark:bg-gray-900/50">
                    <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-100 dark:border-gray-800 p-4 shadow-sm">
                        <pre className="text-sm font-mono leading-relaxed text-blue-600 dark:text-blue-400 overflow-x-auto">
                            {JSON.stringify(data, null, 2)}
                        </pre>
                    </div>
                </div>
                <div className="p-5 border-t border-gray-100 dark:border-gray-700 flex justify-end gap-3">
                    <button
                        onClick={() => {
                            navigator.clipboard.writeText(JSON.stringify(data, null, 2));
                            toast.success('Payload copied to clipboard');
                        }}
                        className="px-4 py-2 text-sm font-medium text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/30 rounded-lg transition-colors"
                    >
                        Copy JSON
                    </button>
                    <button
                        onClick={onClose}
                        className="px-6 py-2 bg-gray-900 dark:bg-white text-white dark:text-gray-900 rounded-lg hover:bg-gray-800 dark:hover:bg-gray-100 font-medium transition-colors"
                    >
                        Close
                    </button>
                </div>
            </div>
        </div>
    );
};

const WebhookLogs = () => {
    const [paymentLogs, setPaymentLogs] = useState([]);
    const [loadingWebhooks, setLoadingWebhooks] = useState(false);
    const [webhookPage, setWebhookPage] = useState(1);
    const [totalWebhookPages, setTotalWebhookPages] = useState(1);
    const [selectedPayload, setSelectedPayload] = useState(null);

    useEffect(() => {
        fetchPaymentLogs();
    }, [webhookPage]);

    const fetchPaymentLogs = async () => {
        try {
            setLoadingWebhooks(true);
            // Using a generic apiClient.get or specific endpoint if defined in auditAPI
            const res = await auditAPI.listPaymentLogs({ page: webhookPage, limit: 20 });
            if (res.logs) {
                setPaymentLogs(res.logs);
                setTotalWebhookPages(res.pages);
            }
        } catch (error) {
            console.error('Failed to fetch payment logs:', error);
            toast.error('Failed to load webhook logs');
        } finally {
            setLoadingWebhooks(false);
        }
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'success': return 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400';
            case 'failed': return 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400';
            case 'duplicate': return 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400';
            case 'ignored': return 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400';
            default: return 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400';
        }
    };

    return (
        <div className="space-y-6">
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-100 dark:border-gray-700 overflow-hidden">
                <div className="p-6 border-b border-gray-100 dark:border-gray-700 flex justify-between items-center bg-gray-50/50 dark:bg-gray-900/50">
                    <div>
                        <h2 className="text-xl font-bold text-gray-800 dark:text-white">CCPayment Webhook Logs</h2>
                        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Audit trail of all incoming payment notifications</p>
                    </div>
                    <button
                        onClick={fetchPaymentLogs}
                        className="p-2 text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/30 rounded-lg transition-colors flex items-center gap-2"
                        disabled={loadingWebhooks}
                    >
                        <RefreshCw className={`w-5 h-5 ${loadingWebhooks ? 'animate-spin' : ''}`} />
                        Refresh
                    </button>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead>
                            <tr className="text-left bg-gray-50 dark:bg-gray-900/50">
                                <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Date & Time</th>
                                <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Order ID</th>
                                <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Type</th>
                                <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Status</th>
                                <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">IP Address</th>
                                <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider text-right">Payload</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
                            {loadingWebhooks ? (
                                Array(5).fill(0).map((_, i) => (
                                    <tr key={i} className="animate-pulse">
                                        <td colSpan="6" className="px-6 py-4"><div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-full"></div></td>
                                    </tr>
                                ))
                            ) : paymentLogs.length > 0 ? (
                                paymentLogs.map((log) => (
                                    <tr key={log._id} className="hover:bg-gray-50 dark:hover:bg-gray-900/30 transition-colors group">
                                        <td className="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">
                                            {new Date(log.created_at).toLocaleString()}
                                        </td>
                                        <td className="px-6 py-4">
                                            <span className="text-sm font-mono text-gray-900 dark:text-white bg-gray-100 dark:bg-gray-700 px-2 py-0.5 rounded">
                                                {log.merchant_order_id}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4">
                                            <span className="text-xs font-medium text-gray-500 dark:text-gray-400 capitalize">
                                                {log.webhook_type.replace(/_/g, ' ')}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4">
                                            <span className={`px-3 py-1 rounded-full text-xs font-bold ${getStatusColor(log.processed_status)} shadow-sm`}>
                                                {log.processed_status}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">
                                            {log.ip_address}
                                        </td>
                                        <td className="px-6 py-4 text-right">
                                            <button
                                                onClick={() => setSelectedPayload(log.payload)}
                                                className="text-blue-600 hover:text-blue-800 dark:hover:text-blue-400 text-sm font-semibold underline decoration-2 underline-offset-4 opacity-0 group-hover:opacity-100 transition-opacity"
                                            >
                                                View JSON
                                            </button>
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="6" className="px-6 py-12 text-center text-gray-500 dark:text-gray-400">
                                        <div className="flex flex-col items-center gap-3">
                                            <Database className="w-12 h-12 text-gray-300" />
                                            <p className="text-lg">No webhook logs found</p>
                                        </div>
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
                {/* Pagination */}
                {totalWebhookPages > 1 && (
                    <div className="p-6 border-t border-gray-100 dark:border-gray-700 flex justify-center gap-2 bg-gray-50/50 dark:bg-gray-900/50">
                        {Array.from({ length: totalWebhookPages }, (_, i) => i + 1).map((p) => (
                            <button
                                key={p}
                                onClick={() => setWebhookPage(p)}
                                className={`w-10 h-10 rounded-lg font-medium transition-all ${webhookPage === p ? 'bg-blue-600 text-white shadow-lg scale-110' : 'bg-white dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 border border-gray-200 dark:border-gray-600'}`}
                            >
                                {p}
                            </button>
                        ))}
                    </div>
                )}
            </div>

            <PayloadModal
                isOpen={!!selectedPayload}
                onClose={() => setSelectedPayload(null)}
                data={selectedPayload}
            />
        </div>
    );
};

export default WebhookLogs;
