import React, { useMemo } from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
  Legend,
} from "chart.js";
import { Bar } from "react-chartjs-2";

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

const WeeksProfit = ({ className = "" }) => {
  const labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

  const data = useMemo(
    () => ({
      labels,
      datasets: [
        {
          label: "Expenses",
          data: [1800, 1300, 1400, 900, 1200, 1600, 1800, 1900, 1700, 2100, 2300, 2500],
          backgroundColor: "#6b7280",
          borderRadius: 6,
          barPercentage: 0.55,
          categoryPercentage: 0.6,
        },
        {
          label: "Profit",
          data: [2300, 1500, 9800, 3600, 4600, 3500, 4200, 5100, 3900, 5200, 6100, 7000],
          backgroundColor: "#2563eb",
          borderRadius: 6,
          barPercentage: 0.55,
          categoryPercentage: 0.6,
        },
      ],
    }),
    []
  );

  const options = useMemo(
    () => ({
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          stacked: false,
          grid: { display: false },
          ticks: { color: "#6b7280" },
        },
        y: {
          stacked: false,
          grid: { color: "rgba(148,163,184,0.25)" },
          ticks: { color: "#6b7280" },
        },
      },
      plugins: {
        legend: {
          position: "bottom",
          labels: { usePointStyle: true, pointStyle: "rectRounded" },
        },
        tooltip: {
          backgroundColor: "#111827",
          borderColor: "#1f2937",
          borderWidth: 1,
          padding: 10,
          callbacks: {
            label: (ctx) => `${ctx.dataset.label}: $${ctx.parsed.y.toLocaleString()}`,
          },
        },
      },
    }),
    []
  );

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 ${className}`}>
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-bold text-gray-800 dark:text-white">Profit vs Expenses</h3>
        <div className="flex space-x-2 text-sm">
          <button className="px-3 py-1 rounded bg-orange-500 text-white">Week</button>
          <button className="px-3 py-1 rounded bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-200">
            Month
          </button>
          <button className="px-3 py-1 rounded bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-200">
            Year
          </button>
        </div>
      </div>

      <div className="h-64">
        <Bar data={data} options={options} />
      </div>
    </div>
  );
};

export default WeeksProfit;