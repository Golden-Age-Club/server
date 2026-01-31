import React from 'react';
import { Header } from './Header';
import { Sidebar, SidebarProvider } from './Sidebar';

const MainLayout = ({ children }) => {
  return (
    <SidebarProvider>
      <div className="flex min-h-screen flex-col">
        <div className="flex flex-1">
          <Sidebar />
          
          <div className="flex-1 bg-gray-100 dark:bg-black">
            <Header />
            
            <main className="isolate w-full max-w-none overflow-hidden p-4 md:p-6 2xl:p-10">
              {children}
            </main>
          </div>
        </div>

        <footer className="bg-gray-100 dark:bg-gray-800 py-4 text-center text-sm text-gray-600 dark:text-gray-400">
          © 2025 SamBuild Dashboard. Built with passion.
        </footer>
      </div>
    </SidebarProvider>
  );
};

export default MainLayout;