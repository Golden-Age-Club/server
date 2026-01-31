import React, { useMemo } from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
} from "chart.js";
import { Line } from "react-chartjs-2";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend);

const PaymentsOverview = ({ className = "" }) => {
  const labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  const values = [3800, 2500, 1900, 2800, 2100, 2600, 3400, 4000, 3700, 4600, 5100, 5900];

  const data = useMemo(
    () => ({
      labels,
      datasets: [
        {
          label: "Revenue",
          data: values,
          fill: true,
          tension: 0.35,
          borderColor: "#3b82f6",
          backgroundColor: (ctx) => {
            const { ctx: canvasCtx, chartArea } = ctx.chart;
            if (!chartArea) return "rgba(59,130,246,0.15)";
            const gradient = canvasCtx.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
            gradient.addColorStop(0, "rgba(59,130,246,0.25)");
            gradient.addColorStop(1, "rgba(59,130,246,0.02)");
            return gradient;
          },
          pointRadius: 3,
          pointBackgroundColor: "#3b82f6",
          pointBorderWidth: 0,
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
          grid: { display: false },
          ticks: { color: "#6b7280" },
        },
        y: {
          grid: { color: "rgba(148,163,184,0.25)" },
          ticks: { color: "#6b7280", callback: (v) => `${v}` },
        },
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: "#111827",
          borderColor: "#1f2937",
          borderWidth: 1,
          padding: 10,
          callbacks: {
            label: (ctx) => `Revenue: $${ctx.parsed.y.toLocaleString()}`,
          },
        },
      },
    }),
    []
  );

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 ${className}`}>
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-bold text-gray-800 dark:text-white">Revenue Overview</h3>
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
        <Line data={data} options={options} />
      </div>
    </div>
  );
};

export default PaymentsOverview;