import { Link } from "react-router-dom";

function Navbar({ onMenuClick, onLogout }) {
  return (
    <header className="sticky top-0 z-20 border-b border-slate-200 bg-white/80 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
        <div className="flex items-center gap-2">
          <button
            type="button"
            className="mr-1 inline-flex items-center justify-center rounded-lg p-2 text-slate-600 hover:bg-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500 md:hidden"
            onClick={onMenuClick}
          >
            <span className="sr-only">Open sidebar</span>
            <svg
              className="h-5 w-5"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1.5}
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5"
              />
            </svg>
          </button>
          <Link to="/dashboard" className="inline-flex items-center gap-2">
            <span className="flex h-8 w-8 items-center justify-center rounded-xl bg-indigo-600 text-sm font-semibold text-white shadow-md">
              SJ
            </span>
            <span className="text-base font-semibold text-slate-900 sm:text-lg">
              Secure Job Platform
            </span>
          </Link>
        </div>

        <div className="flex items-center gap-3">
          <Link
            to="/profile"
            className="hidden text-sm font-medium text-slate-600 hover:text-indigo-600 sm:inline-flex"
          >
            Profile
          </Link>
          <button
            type="button"
            onClick={onLogout}
            className="inline-flex items-center justify-center rounded-lg bg-indigo-600 px-3 py-1.5 text-sm font-medium text-white shadow-sm transition hover:bg-indigo-700"
          >
            Logout
          </button>
        </div>
      </div>
    </header>
  );
}

export default Navbar;

