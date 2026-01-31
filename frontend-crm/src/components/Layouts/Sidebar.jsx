/* eslint-disable react-refresh/only-export-components */
import React, { useMemo, useState, createContext, useContext } from 'react';
import { NavLink, useLocation } from "react-router-dom";
import { useAuth } from "../../auth/AuthContext";

// Icon Components
const HomeIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="size-6">
    <path strokeLinecap="round" strokeLinejoin="round" d="m2.25 12 8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25" />
  </svg>
);

const Calendar = () => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="size-6">
    <path strokeLinecap="round" strokeLinejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 0 1 2.25-2.25h13.5A2.25 2.25 0 0 1 21 7.5v11.25m-18 0A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75m-18 0v-7.5A2.25 2.25 0 0 1 5.25 9h13.5A2.25 2.25 0 0 1 21 11.25v7.5" />
  </svg>
);

const User = () => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="size-6">
    <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z" />
  </svg>
);

const Alphabet = () => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="size-6">
    <path strokeLinecap="round" strokeLinejoin="round" d="M7.5 14.25v2.25m3-4.5v4.5m3-6.75v6.75m3-9v9M6 20.25h12A2.25 2.25 0 0 0 20.25 18V6A2.25 2.25 0 0 0 18 3.75H6A2.25 2.25 0 0 0 3.75 6v12A2.25 2.25 0 0 0 6 20.25Z" />
  </svg>
);

const Table = () => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="size-6">
    <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25H12" />
  </svg>
);

const PieChart = () => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="size-6">
    <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 6a7.5 7.5 0 1 0 7.5 7.5h-7.5V6Z" />
    <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 10.5H21A7.5 7.5 0 0 0 13.5 3v7.5Z" />
  </svg>
);

const FourCircle = () => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="size-6">
    <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 6.75h12M8.25 12h12m-12 5.25h12M3.75 6.75h.007v.008H3.75V6.75Zm.375 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0ZM3.75 12h.007v.008H3.75V12Zm.375 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm-.375 5.25h.007v.008H3.75v-.008Zm.375 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Z" />
  </svg>
);

const Authentication = () => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="size-6">
    <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 5.25a3 3 0 0 1 3 3m3 0a6 6 0 0 1-7.029 5.912c-.563-.097-1.159.026-1.563.43L10.5 17.25H8.25v2.25H6v2.25H2.25v-2.818c0-.597.237-1.17.659-1.591l6.499-6.499c.404-.404.527-1 .43-1.563A6 6 0 1 1 21.75 8.25Z" />
  </svg>
);

const ArrowLeftIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="size-7">
    <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 19.5 3 12m0 0 7.5-7.5M3 12h18" />
  </svg>
);

const ChevronUp = ({ className }) => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className={`size-5 ${className}`}>
    <path strokeLinecap="round" strokeLinejoin="round" d="m4.5 15.75 7.5-7.5 7.5 7.5" />
  </svg>
);

// Define the context for sidebar state
const SidebarContext = createContext();

// Custom hook to use the sidebar context
export const useSidebarContext = () => {
  const context = useContext(SidebarContext);
  if (!context) {
    throw new Error('useSidebarContext must be used within a SidebarProvider');
  }
  return context;
};

// Provider component
export const SidebarProvider = ({ children }) => {
  const [isOpen, setIsOpen] = useState(true);
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);

  React.useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 768);
      if (window.innerWidth >= 768) {
        setIsOpen(true);
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const toggleSidebar = () => {
    setIsOpen(!isOpen);
  };

  return (
    <SidebarContext.Provider value={{ isOpen, setIsOpen, isMobile, toggleSidebar }}>
      {children}
    </SidebarContext.Provider>
  );
};

// Navigation Data
const NAV_DATA = [
  {
    label: "ADMIN",
    items: [
      {
        title: "Dashboard",
        icon: HomeIcon,
        permission: "dashboard",
        items: [{ title: "Overview", url: "/" }],
      },
      { title: "User Management", url: "/users", icon: User, items: [], permission: "users" },
      { title: "Wallet & Finance", url: "/finance", icon: Table, items: [], permission: "finance" },
      { title: "Machine Management", url: "/machines", icon: Alphabet, items: [], permission: "games" },
      { title: "VIP & Segmentation", url: "/vip", icon: Calendar, items: [], permission: "vip" },
    ],
  },
  {
    label: "OPERATIONS",
    items: [
      {
        title: "Risk Control",
        icon: PieChart,
        permission: "risk",
        items: [{ title: "Abnormal Users", url: "/risk" }],
      },
      {
        title: "Bonus & Promotions",
        icon: FourCircle,
        permission: "promotions",
        items: [{ title: "Campaigns", url: "/promotions" }],
      },
      {
        title: "Reports",
        icon: PieChart,
        permission: "reports",
        items: [{ title: "Core Metrics", url: "/reports" }],
      },
      {
        title: "System & Logs",
        icon: Authentication,
        permission: "system",
        items: [{ title: "Settings", url: "/system" }],
      },
    ],
  },
];

// MenuItem Component
const MenuItem = ({ children, isActive, onClick, as = 'button', href, className = '', onNavigate }) => {
  const menuItemClasses = `flex items-center gap-3 py-3 px-4 rounded-lg transition-colors ${isActive
      ? 'bg-orange-500 text-white'
      : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700'
    }`;

  if (as === 'link' && href) {
    return (
      <NavLink
        to={href}
        onClick={onNavigate}
        className={({ isActive: navActive }) => `${menuItemClasses} ${navActive ? 'bg-orange-500 text-white' : ''} ${className}`}
      >
        {children}
      </NavLink>
    );
  }

  return (
    <button
      onClick={onClick}
      className={`${menuItemClasses} ${className}`}
      type="button"
    >
      {children}
    </button>
  );
};

// Logo Component
const Logo = () => (
  <div className="flex items-center gap-2">
    <div className="w-8 h-8 bg-orange-500 rounded-md"></div>
    <span className="text-xl font-bold text-gray-800 dark:text-white">Golden Cash Casino</span>
  </div>
);

const Sidebar = () => {
  const { isOpen, setIsOpen, isMobile, toggleSidebar } = useSidebarContext();
  const [expandedItems, setExpandedItems] = useState([]);
  const { permissions } = useAuth();
  const location = useLocation();

  const navSections = useMemo(() => {
    const hasPerm = (item) => !item.permission || permissions.includes(item.permission);

    return NAV_DATA
      .map((section) => ({
        ...section,
        items: section.items.filter(hasPerm),
      }))
      .filter((section) => section.items.length);
  }, [permissions]);

  const toggleExpanded = (title) => {
    setExpandedItems((prev) =>
      prev.includes(title) ? prev.filter((t) => t !== title) : [title]
    );
  };

  return (
    <>
      {/* Mobile Overlay */}
      {isMobile && isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 transition-opacity duration-300"
          onClick={() => setIsOpen(false)}
          aria-hidden="true"
        />
      )}

      <aside
        className={`overflow-hidden border-r border-gray-200 bg-white transition-[width] duration-200 ease-linear dark:border-gray-800 dark:bg-gray-900 ${isMobile ? "fixed bottom-0 top-0 z-50" : "sticky top-0 h-screen"
          } ${isOpen ? "w-64" : "w-0"}`}
        aria-label="Main navigation"
        aria-hidden={!isOpen}
        inert={!isOpen}
      >
        <div className="flex h-full flex-col py-6 pl-6 pr-2">
          <div className="relative pr-4.5">
            <a
              href="/"
              onClick={() => isMobile && toggleSidebar()}
              className="px-0 py-2.5 min-[850px]:py-0"
            >
              <Logo />
            </a>

            {isMobile && (
              <button
                onClick={toggleSidebar}
                className="absolute left-3/4 right-4.5 top-1/2 -translate-y-1/2 text-right"
              >
                <span className="sr-only">Close Menu</span>
                <ArrowLeftIcon className="ml-auto size-7" />
              </button>
            )}
          </div>

          {/* Navigation */}
          <div className="custom-scrollbar mt-6 flex-1 overflow-y-auto pr-3 min-[850px]:mt-10">
            {navSections.map((section) => (
              <div key={section.label} className="mb-6">
                <h2 className="mb-5 text-sm font-medium text-gray-500 dark:text-gray-400">
                  {section.label}
                </h2>

                <nav role="navigation" aria-label={section.label}>
                  <ul className="space-y-2">
                    {section.items.map((item) => (
                      <li key={item.title}>
                        {item.items.length ? (
                          <div>
                            <MenuItem
                              isActive={item.items.some(
                                ({ url }) => location.pathname === url
                              )}
                              onClick={() => toggleExpanded(item.title)}
                            >
                              <item.icon
                                className="size-6 shrink-0"
                                aria-hidden="true"
                              />

                              <span>{item.title}</span>

                              <ChevronUp
                                className={`ml-auto rotate-180 transition-transform duration-200 ${expandedItems.includes(item.title) ? "rotate-0" : ""
                                  }`}
                                aria-hidden="true"
                              />
                            </MenuItem>

                            {expandedItems.includes(item.title) && (
                              <ul
                                className="ml-9 mr-0 space-y-1.5 pb-[15px] pr-0 pt-2"
                                role="menu"
                              >
                                {item.items.map((subItem) => (
                                  <li key={subItem.title} role="none">
                                    <MenuItem
                                      as="link"
                                      href={subItem.url}
                                      onNavigate={() => isMobile && toggleSidebar()}
                                      isActive={location.pathname === subItem.url}
                                    >
                                      <span>{subItem.title}</span>
                                    </MenuItem>
                                  </li>
                                ))}
                              </ul>
                            )}
                          </div>
                        ) : (
                          (() => {
                            const href =
                              "url" in item
                                ? item.url + ""
                                : "/" +
                                item.title.toLowerCase().split(" ").join("-");

                            return (
                              <MenuItem
                                className="flex items-center gap-3 py-3 px-4"
                                as="link"
                                href={href}
                                onNavigate={() => isMobile && toggleSidebar()}
                                isActive={location.pathname === href}
                              >
                                <item.icon
                                  className="size-6 shrink-0"
                                  aria-hidden="true"
                                />

                                <span>{item.title}</span>
                              </MenuItem>
                            );
                          })()
                        )}
                      </li>
                    ))}
                  </ul>
                </nav>
              </div>
            ))}
          </div>
        </div>
      </aside>
    </>
  );
};

export { Sidebar };