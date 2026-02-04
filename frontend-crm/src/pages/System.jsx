import React, { useState, useEffect } from "react";
import { auditAPI, adminAPI } from "../api/client";
import { History, Shield, Users, Activity, Settings } from "lucide-react";
import WebhookLogs from "./WebhookLogs";
import { useTranslation } from 'react-i18next';

export default function SystemPage() {
    const { t } = useTranslation();
    const [logs, setLogs] = useState([]);
    const [admins, setAdmins] = useState([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState("audit");
    const [filters, setFilters] = useState({
        page: 1,
        page_size: 20
    });

    const fetchLogs = async () => {
        setLoading(true);
        try {
            const response = await auditAPI.listLogs(filters);
            if (response.success) {
                setLogs(response.data || []);
            }
        } catch (err) {
            console.error("Failed to fetch audit logs:", err);
        } finally {
            setLoading(false);
        }
    };

    const fetchAdmins = async () => {
        try {
            const response = await adminAPI.list();
            if (response.success) {
                setAdmins(response.data || []);
            }
        } catch (err) {
            console.error("Failed to fetch admins:", err);
        }
    };

    useEffect(() => {
        if (activeTab === "audit") fetchLogs();
        if (activeTab === "admins") fetchAdmins();
    }, [activeTab, filters.page]);

    const getLevelColor = (level) => {
        switch (level) {
            case "CRITICAL": return "text-red-600 bg-red-100";
            case "WARN": return "text-yellow-600 bg-yellow-100";
            default: return "text-blue-600 bg-blue-100";
        }
    };

    return (
        <div className="p-4 md:p-6">
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                    {t('system.title', 'System & Administration')}
                </h1>
                <p className="mt-1 text-gray-600 dark:text-gray-400">
                    {t('system.subtitle', 'Manage platform logs and administrative staff.')}
                </p>
            </div>

            {/* Tabs */}
            <div className="mb-6 border-b border-gray-200 dark:border-gray-700">
                <div className="flex gap-8">
                    <button
                        onClick={() => setActiveTab("audit")}
                        className={`flex items-center gap-2 pb-4 text-sm font-medium transition-colors ${activeTab === "audit"
                            ? "border-b-2 border-primary text-primary"
                            : "text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
                            }`}
                    >
                        <History className="h-4 w-4" />
                        {t('system.logs.title', 'Audit Logs')}
                    </button>
                    <button
                        onClick={() => setActiveTab("webhooks")}
                        className={`flex items-center gap-2 pb-4 text-sm font-medium transition-colors ${activeTab === "webhooks"
                            ? "border-b-2 border-primary text-primary"
                            : "text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
                            }`}
                    >
                        <Activity className="h-4 w-4" />
                        Webhook Logs
                    </button>
                    <button
                        onClick={() => setActiveTab("admins")}
                        className={`flex items-center gap-2 pb-4 text-sm font-medium transition-colors ${activeTab === "admins"
                            ? "border-b-2 border-primary text-primary"
                            : "text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
                            }`}
                    >
                        <Shield className="h-4 w-4" />
                        {t('admin_management.title', 'Admin Team')}
                    </button>
                </div>
            </div>

            {activeTab === "audit" ? (
                <div className="overflow-x-auto rounded-lg bg-white shadow-md dark:bg-gray-800">
                    <table className="w-full text-left text-sm text-gray-500 dark:text-gray-400">
                        <thead className="bg-gray-50 text-xs uppercase text-gray-700 dark:bg-gray-700 dark:text-gray-400">
                            <tr>
                                <th className="px-6 py-3">Timestamp</th>
                                <th className="px-6 py-3">Admin</th>
                                <th className="px-6 py-3">Action</th>
                                <th className="px-6 py-3">Resource</th>
                                <th className="px-6 py-3">IP Address</th>
                                <th className="px-6 py-3">Level</th>
                            </tr>
                        </thead>
                        <tbody>
                            {loading ? (
                                <tr>
                                    <td colSpan="6" className="px-6 py-10 text-center">Loading audit history...</td>
                                </tr>
                            ) : logs.length === 0 ? (
                                <tr>
                                    <td colSpan="6" className="px-6 py-10 text-center">No logs found.</td>
                                </tr>
                            ) : (
                                logs.map((log, index) => (
                                    <tr key={log.id || index} className="border-b bg-white hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:hover:bg-gray-600">
                                        <td className="px-6 py-4 text-xs">
                                            {new Date(log.timestamp).toLocaleString('en-GB', {
                                                month: 'short',
                                                day: '2-digit',
                                                hour: '2-digit',
                                                minute: '2-digit',
                                                second: '2-digit'
                                            }).replace(',', '')}
                                        </td>
                                        <td className="px-6 py-4">
                                            <div className="font-medium text-gray-900 dark:text-white">{log.admin_username}</div>
                                            <div className="text-xs text-gray-500 font-mono">{log.admin_id}</div>
                                        </td>
                                        <td className="px-6 py-4">{log.action}</td>
                                        <td className="px-6 py-4">
                                            <span className="text-xs font-mono">{log.resource_type}: {log.resource_id}</span>
                                        </td>
                                        <td className="px-6 py-4 text-xs font-mono">{log.ip_address}</td>
                                        <td className="px-6 py-4">
                                            <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${getLevelColor(log.level)}`}>
                                                {log.level}
                                            </span>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            ) : activeTab === "webhooks" ? (
                <WebhookLogs />
            ) : (
                <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                    {admins.map((admin) => (
                        <div key={admin.admin_id} className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-700 dark:bg-gray-800">
                            <div className="flex items-center justify-between mb-4">
                                <div className="flex items-center gap-3">
                                    <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 dark:bg-blue-900 dark:text-blue-300">
                                        <Users className="h-6 w-6" />
                                    </div>
                                    <div>
                                        <h3 className="font-bold text-gray-900 dark:text-white">{admin.username}</h3>
                                        <p className="text-xs text-gray-500">{admin.email}</p>
                                    </div>
                                </div>
                                <span className={`px-2 py-1 rounded-full text-[10px] font-bold ${admin.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                                    }`}>
                                    {admin.status.toUpperCase()}
                                </span>
                            </div>
                            <div className="space-y-2">
                                <div className="flex text-xs justify-between">
                                    <span className="text-gray-500">Roles:</span>
                                    <span className="font-medium text-gray-700 dark:text-gray-300">{admin.roles.join(", ")}</span>
                                </div>
                                <div className="flex text-xs justify-between">
                                    <span className="text-gray-500">MFA:</span>
                                    <span className={admin.mfa_enabled ? "text-green-600 font-bold" : "text-gray-400"}>
                                        {admin.mfa_enabled ? "ENABLED" : "DISABLED"}
                                    </span>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
