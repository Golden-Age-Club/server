import React, { useState, useEffect } from "react";
import { promotionsAPI } from "../api/client";

export default function PromotionsPage() {
    const [promos, setPromos] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchPromos = async () => {
        setLoading(true);
        try {
            const response = await promotionsAPI.list();
            if (response.success) setPromos(response.data);
        } catch (err) {
            console.error("Failed to fetch promotions:", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchPromos();
    }, []);

    return (
        <div className="p-4 md:p-6">
            <div className="mb-6 flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Promotions</h1>
                    <p className="mt-1 text-gray-600 dark:text-gray-400">Build and manage marketing campaigns.</p>
                </div>
                <button className="rounded-md bg-primary py-2 px-6 text-white hover:bg-opacity-90 font-semibold">
                    New Promotion
                </button>
            </div>

            <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
                {promos.length === 0 ? (
                    <div className="col-span-full py-20 text-center bg-white dark:bg-gray-800 rounded-lg shadow-md">
                        <p className="text-gray-500">No promotions found. Create your first campaign!</p>
                    </div>
                ) : (
                    promos.map(promo => (
                        <div key={promo.promo_id} className="rounded-lg bg-white p-6 shadow-md dark:bg-gray-800 border-l-4 border-primary">
                            <h2 className="text-xl font-bold dark:text-white">{promo.name}</h2>
                            <p className="mt-2 text-sm text-gray-600 dark:text-gray-400 line-clamp-2">{promo.description}</p>

                            <div className="mt-4 grid grid-cols-2 gap-2 text-xs uppercase font-bold text-gray-500">
                                <div>Bonus</div>
                                <div>Wagering</div>
                                <div className="text-gray-900 dark:text-white">{promo.bonus_percent}%</div>
                                <div className="text-gray-900 dark:text-white">{promo.wagering_requirement}x</div>
                            </div>

                            <div className="mt-6 flex items-center justify-between">
                                <span className={`rounded-full px-3 py-1 text-xs font-semibold ${promo.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                                    {promo.status}
                                </span>
                                <button className="text-primary text-sm font-medium hover:underline">Edit Rules</button>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}
