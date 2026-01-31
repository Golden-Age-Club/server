import React from "react";
import OverviewCardsGroup from "../components/OverviewCards";
import PaymentsOverview from "../components/Charts/PaymentsOverview";
import WeeksProfit from "../components/Charts/WeeksProfit";

export default function DashboardOverview() {
  return (
    <>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-800 dark:text-white">
          Welcome to Golden Cash Casino Admin Dashboard
        </h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Monitor players, bets, games, risk, bonus, and finance in one place.
        </p>
      </div>

      <OverviewCardsGroup />

      <div className="mt-4 grid grid-cols-12 gap-4 md:mt-6 md:gap-6 2xl:mt-9 2xl:gap-7.5">
        <PaymentsOverview className="col-span-12 xl:col-span-7" />

        <WeeksProfit className="col-span-12 xl:col-span-5" />
      </div>
    </>
  );
}

