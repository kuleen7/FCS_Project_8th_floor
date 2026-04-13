import { Fragment } from "react";
import { NavLink } from "react-router-dom";

const navByRole = {
  user: [
    { to: "/dashboard", label: "Dashboard" },
    { to: "/profile", label: "Profile" },
    { to: "/jobs/search", label: "Job Search" },
    { to: "/applications", label: "Applications" },
    { to: "/messages", label: "Messages" },
    { to: "/resumes", label: "Resumes" },
  ],
  recruiter: [
    { to: "/dashboard", label: "Dashboard" },
    { to: "/company", label: "Company" },
    { to: "/jobs", label: "Job Management" },
    { to: "/applications", label: "Applicants" },
    { to: "/messages", label: "Messages" },
    { to: "/resumes", label: "Resumes" },
  ],
  admin: [
    { to: "/dashboard", label: "Dashboard" },
    { to: "/admin/users", label: "User Management" },
    { to: "/admin/system", label: "System" },
    { to: "/admin/audit", label: "Audit Logs" },
    { to: "/messages", label: "Messages" },
  ],
};

function SidebarLink({ to, label, onClick }) {
  return (
    <NavLink
      to={to}
      onClick={onClick}
      className={({ isActive }) =>
        [
          "flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
          isActive
            ? "bg-indigo-50 text-indigo-700"
            : "text-slate-600 hover:bg-slate-50 hover:text-slate-900",
        ].join(" ")
      }
    >
      <span className="h-1.5 w-1.5 rounded-full bg-current" />
      <span>{label}</span>
    </NavLink>
  );
}

function Sidebar({ open, onClose, onLogout }) {
  let role = "user";
  try {
    role = JSON.parse(localStorage.getItem("user") || "{}").role || "user";
  } catch {
    role = "user";
  }
  const navItems = navByRole[role] || navByRole.user;

  return (
    <Fragment>
      {/* Mobile overlay */}
      {open && (
        <div
          className="fixed inset-0 z-30 bg-slate-900/40 md:hidden"
          onClick={onClose}
        />
      )}

      <aside
        className={`fixed inset-y-0 left-0 z-40 w-64 transform bg-white shadow-md transition-transform md:static md:inset-auto md:translate-x-0 md:shadow-none ${
          open ? "translate-x-0" : "-translate-x-full md:translate-x-0"
        }`}
      >
        <div className="flex h-full flex-col border-r border-slate-200">
          <div className="flex items-center justify-between px-4 py-4 md:hidden">
            <span className="text-sm font-semibold text-slate-900">
              Navigation
            </span>
            <button
              type="button"
              onClick={onClose}
              className="inline-flex items-center justify-center rounded-lg p-1.5 text-slate-500 hover:bg-slate-100"
            >
              <span className="sr-only">Close sidebar</span>
              <svg
                className="h-4 w-4"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={1.5}
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M6 18 18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>

          <nav className="flex-1 space-y-1 px-3 py-4">
            {navItems.map((item) => (
              <SidebarLink
                key={item.to}
                to={item.to}
                label={item.label}
                onClick={onClose}
              />
            ))}
          </nav>

          <div className="border-t border-slate-200 px-3 py-4">
            <button
              type="button"
              onClick={onLogout}
              className="flex w-full items-center justify-center rounded-lg bg-slate-100 px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-200"
            >
              Logout
            </button>
          </div>
        </div>
      </aside>
    </Fragment>
  );
}

export default Sidebar;

