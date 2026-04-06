import { Navbar } from "@/components/Navbar/navbar";
import { Sidebar } from "@/components/Sidebar/Sidebar";
import { useState } from "react";

import { Outlet } from "react-router-dom";

const MainLayout = () => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  return (
    <div className="bg-background">
      <Navbar onMenuClick={() => setIsSidebarOpen(true)} />
      <Sidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} />
      <main className="p-20">
        <Outlet />
      </main>
    </div>
  );
};

export default MainLayout;
