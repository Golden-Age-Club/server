import React, { useState, useEffect } from "react";
import { riskAPI } from "../api/client";

export default function RiskPage() {
    const [rules, setRules] = useState([]);
    const [alerts, setAlerts] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchData = async () => {
        setLoading(true);
        try {
            const [rulesRes, alertsRes] = await Promise.all([
                riskAPI.getRules(),
                riskAPI.getAlerts()
            ]);
            if (rulesRes.success) setRules(rulesRes.data);
            if (alertsRes.success) setAlerts(alertsRes.data);
        } catch (err) {
            console.error("Failed to fetch risk data:", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    return (
        <div className="p-4 md:p-6">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Risk Control</h1>
            <p className="mt-1 text-gray-600 dark:text-gray-400">Manage security rules and monitor suspicious activities.</p>

            <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
                {/* Rules Section */}
                <div className="rounded-lg bg-white p-6 shadow-md dark:bg-gray-800">
                    <h2 className="mb-4 text-xl font-bold dark:text-white">Active Rules</h2>
                    <div className="space-y-4">
                        {rules.map(rule => (
                            <div key={rule.rule_id} className="flex items-center justify-between border-b dark:border-gray-700 pb-3 last:border-0">
                                <div>
                                    <div className="font-semibold text-gray-900 dark:text-white">{rule.description}</div>
                                    <div className="text-sm text-gray-500">Action: <span className="uppercase text-orange-600">{rule.action}</span></div>
                                </div>
                                <div className="text-right">
                                    <span className={`rounded-full px-2 py-1 text-xs font-bold ${rule.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                                        {rule.is_active ? 'ACTIVE' : 'DISABLED'}
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Alerts Section */}
                <div className="rounded-lg bg-white p-6 shadow-md dark:bg-gray-800">
                    <h2 className="mb-4 text-xl font-bold dark:text-white">Recent Alerts</h2>
                    <div className="overflow-x-auto">
                        <table className="w-full text-left text-sm text-gray-500 dark:text-gray-400">
                            <thead className="bg-gray-50 text-xs uppercase text-gray-700 dark:bg-gray-700 dark:text-gray-400">
                                <tr>
                                    <th className="px-4 py-3">Player</th>
                                    <th className="px-4 py-3">Issue</th>
                                    <th className="px-4 py-3">Detected</th>
                                </tr>
                            </thead>
                            <tbody>
                                {alerts.length === 0 ? (
                                    <tr><td colSpan="3" className="py-10 text-center">No risk alerts detected.</td></tr>
                                ) : (
                                    alerts.map(alert => (
                                        <tr key={alert.alert_id} className="border-b dark:border-gray-700">
                                            <td className="px-4 py-3 font-medium text-gray-900 dark:text-white">{alert.player_id}</td>
                                            <td className="px-4 py-3">{alert.rule_type}</td>
                                            <td className="px-4 py-3">{new Date(alert.created_at).toLocaleString()}</td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
}
