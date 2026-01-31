import React, { useState, useEffect } from 'react';
import { statsAPI } from '../api/client';

// Icon Components for Overview Cards (unchanged)
const ViewsIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
    <path strokeLinecap="round" strokeLinejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" />
    <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
  </svg>
);

const ProfitIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
    <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 18 9 11.25l4.306 4.306a11.95 11.95 0 0 1 5.814-5.518l2.74-1.22m0 0-5.94-2.281m5.94 2.28-2.28 5.941" />
  </svg>
);

const ProductIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
    <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 10.5V6a3.75 3.75 0 1 0-7.5 0v4.5m11.356-1.993 1.263 12c.07.665-.45 1.243-1.119 1.243H4.25a1.125 1.125 0 0 1-1.12-1.243l1.264-12A1.125 1.125 0 0 1 5.513 7.5h12.974c.576 0 1.059.435 1.119 1.007ZM8.625 10.5a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm7.5 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Z" />
  </svg>
);

const UsersIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
    <path strokeLinecap="round" strokeLinejoin="round" d="M15 19.128a9.38 9.38 0 0 0 2.625.372 9.337 9.337 0 0 0 4.121-.952 4.125 4.125 0 0 0-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 0 1 8.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0 1 11.964-3.07M12 6.375a3.375 3.375 0 1 1-6.75 0 3.375 3.375 0 0 1 6.75 0Zm8.25 2.25a2.625 2.625 0 1 1-5.25 0 2.625 2.625 0 0 1 5.25 0Z" />
  </svg>
);

// Individual Overview Card Component
const OverviewCard = ({ label, data, icon, loading }) => {
  const isPositive = data?.is_positive ?? true;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-500 dark:text-gray-400 text-sm">{label}</p>
          {loading ? (
            <div className="h-8 w-24 bg-gray-200 dark:bg-gray-700 animate-pulse rounded mt-1"></div>
          ) : (
            <h3 className="text-2xl font-bold text-gray-800 dark:text-white mt-1">{data?.value || "0"}</h3>
          )}
        </div>
        <div className={`p-3 rounded-full ${isPositive ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'}`}>
          {icon}
        </div>
      </div>

      <div className="mt-4 flex items-center">
        {loading ? (
          <div className="h-4 w-16 bg-gray-200 dark:bg-gray-700 animate-pulse rounded"></div>
        ) : (
          <>
            <span className={`text-sm ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
              {isPositive ? '+' : ''}{data?.percentage || "0"}%
            </span>
            <span className="text-gray-500 dark:text-gray-400 text-sm ml-2">from last week</span>
          </>
        )}
      </div>
    </div>
  );
};

// Overview Cards Group Component
const OverviewCardsGroup = () => {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState({
    ggr: { value: "$0.00", percentage: 0, is_positive: true },
    rtp: { value: "0%", percentage: 0, is_positive: true },
    dau: { value: "0", percentage: 0, is_positive: true },
    bets: { value: "0", percentage: 0, is_positive: true },
    total_players: { value: "0", percentage: 0, is_positive: true },
  });

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await statsAPI.getOverview();
        if (response.success && response.data) {
          setData(response.data);
        }
      } catch (error) {
        console.error("Failed to fetch dashboard stats:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  return (
    <div className="grid gap-4 sm:grid-cols-2 sm:gap-6 xl:grid-cols-4 2xl:gap-7.5">
      <OverviewCard
        label="Total GGR"
        data={data.ggr}
        icon={<ProfitIcon />}
        loading={loading}
      />

      <OverviewCard
        label="RTP"
        data={data.rtp}
        icon={<ViewsIcon />}
        loading={loading}
      />

      <OverviewCard
        label="Total Players"
        data={data.total_players}
        icon={<UsersIcon />}
        loading={loading}
      />

      <OverviewCard
        label="Active Users (DAU)"
        data={data.dau}
        icon={<UsersIcon />}
        loading={loading}
      />

      <OverviewCard
        label="Total Bets"
        data={data.bets}
        icon={<ProductIcon />}
        loading={loading}
      />
    </div>
  );
};

export default OverviewCardsGroup;