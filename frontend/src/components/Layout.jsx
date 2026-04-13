import { useState } from "react";
import { Outlet, useNavigate } from "react-router-dom";
import Navbar from "./Navbar";
import Sidebar from "./Sidebar";

function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    navigate("/login", { replace: true });
  };

  return (
    <div className="flex min-h-screen flex-col bg-gradient-to-b from-slate-50 to-indigo-50/40">
      <Navbar
        onMenuClick={() => setSidebarOpen(true)}
        onLogout={handleLogout}
      />
      <div className="mx-auto flex w-full max-w-6xl flex-1 px-4 pb-6 pt-4 sm:px-6 lg:px-8">
        <Sidebar
          open={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
          onLogout={handleLogout}
        />
        <main className="ml-0 flex-1 md:ml-64">
          <div className="h-full rounded-2xl border border-slate-200/70 bg-white/95 p-6 shadow-lg backdrop-blur md:ml-6">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}

export default Layout;

