import React from 'react';
import { useSidebarContext } from './Sidebar';

// Icon Components
const SearchIcon = ({ className = "" }) => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className={`size-5 ${className}`}>
    <path strokeLinecap="round" strokeLinejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
  </svg>
);

const MenuIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="size-6">
    <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
  </svg>
);

const NotificationIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="size-6">
    <path strokeLinecap="round" strokeLinejoin="round" d="M14.857 17.082a23.848 23.848 0 0 0 5.454-1.31A8.967 8.967 0 0 1 18 9.75V9A6 6 0 0 0 6 9v.75a8.967 8.967 0 0 1-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 0 1-5.714 0m5.714 0a3 3 0 1 1-5.714 0" />
  </svg>
);

const ThemeToggleIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="size-6">
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 3v2.25m6.364.386-1.591 1.591M21 12h-2.25m-.386 6.364-1.591-1.591M12 18.75V21m-4.773-4.227-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636M15.75 12a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0Z" />
  </svg>
);

const UserAvatar = () => (
  <div className="w-10 h-10 rounded-full bg-gray-200 border-2 border-gray-300 flex items-center justify-center text-gray-700 font-medium">
    U
  </div>
);

// Notification Component
const Notification = () => (
  <div className="relative">
    <button className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700">
      <NotificationIcon />
    </button>
    <span className="absolute top-0 right-0 w-2 h-2 bg-red-500 rounded-full"></span>
  </div>
);

// Theme Toggle Component
const ThemeToggleSwitch = () => (
  <button className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700">
    <ThemeToggleIcon />
  </button>
);

// User Info Component
const UserInfo = () => (
  <div className="flex items-center gap-3">
    <div className="text-left hidden sm:block">
      <p className="text-sm font-medium text-gray-800 dark:text-white">Admin User</p>
      <p className="text-xs text-gray-500 dark:text-gray-400">Administrator</p>
    </div>
    <UserAvatar />
  </div>
);

export const Header = () => {
  const { toggleSidebar, isMobile } = useSidebarContext();

  return (
    <header className="sticky top-0 z-30 flex items-center justify-between border-b border-gray-200 bg-white px-4 py-5 shadow-sm dark:border-gray-700 dark:bg-gray-800 md:px-5">
      <button
        onClick={toggleSidebar}
        className="rounded-lg border px-1.5 py-1 dark:border-gray-700 dark:bg-gray-700 hover:dark:bg-gray-600 lg:hidden"
      >
        <MenuIcon />
        <span className="sr-only">Toggle Sidebar</span>
      </button>

      {isMobile && (
        <a href="/" className="ml-2 max-[430px]:hidden min-[375px]:ml-4">
          <div className="w-8 h-8 bg-orange-500 rounded-md"></div>
        </a>
      )}

      <div className="max-xl:hidden">
        <h1 className="mb-0.5 text-2xl font-bold text-gray-800 dark:text-white">
          Dashboard
        </h1>
        <p className="font-medium text-gray-600 dark:text-gray-300">
          Slot Machine Admin Console for players, bets, games, and risk.
        </p>
      </div>

      <div className="flex flex-1 items-center justify-end gap-2 min-[375px]:gap-4">
        <div className="w-full max-w-[360px]">
          <div className="flex items-center rounded-full border border-gray-300 bg-gray-50 px-4 py-2.5 text-sm text-gray-700 shadow-sm focus-within:border-orange-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:focus-within:border-orange-500">
            <SearchIcon className="mr-3 text-gray-400" />
            <input
              type="search"
              placeholder="Search"
              className="w-full bg-transparent outline-none placeholder:text-gray-400 dark:placeholder:text-gray-500"
            />
          </div>
        </div>

        <Notification />

        <div className="shrink-0">
          <UserInfo />
        </div>
      </div>
    </header>
  );
};