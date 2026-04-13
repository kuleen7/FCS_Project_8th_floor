import { Link } from "react-router-dom";

function HomePage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
      <div className="mx-auto flex w-full max-w-5xl flex-col items-center gap-10 text-center md:flex-row md:items-stretch md:text-left">
        <div className="flex-1 space-y-6">
          <p className="inline-flex rounded-full bg-indigo-50 px-3 py-1 text-xs font-medium uppercase tracking-wide text-indigo-700">
            Secure Job Search Platform
          </p>
          <h1 className="text-3xl font-semibold tracking-tight text-slate-900 sm:text-4xl lg:text-5xl">
            Find your next role with{" "}
            <span className="text-indigo-600">enterprise‑grade security</span>.
          </h1>
          <p className="max-w-xl text-sm leading-relaxed text-slate-600 sm:text-base">
            A modern dashboard for managing your profile, resumes, and job
            applications. Built for security‑first organizations and candidates.
          </p>
          <div className="flex flex-col items-center gap-3 sm:flex-row sm:justify-start">
            <Link
              to="/register"
              className="inline-flex w-full items-center justify-center rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-medium text-white shadow-md transition hover:bg-indigo-700 sm:w-auto"
            >
              Get started
            </Link>
            <Link
              to="/login"
              className="inline-flex w-full items-center justify-center rounded-lg border border-slate-200 px-5 py-2.5 text-sm font-medium text-slate-700 shadow-sm transition hover:border-indigo-200 hover:bg-indigo-50 sm:w-auto"
            >
              Sign in
            </Link>
          </div>
        </div>

        <div className="flex-1">
          <div className="mx-auto w-full max-w-md rounded-2xl bg-white p-6 shadow-md">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <h2 className="text-sm font-semibold text-slate-900">
                  Secure candidate workspace
                </h2>
                <p className="text-xs text-slate-500">
                  Encrypted profiles, verified resumes, and audited access.
                </p>
              </div>
              <span className="inline-flex items-center rounded-full bg-emerald-50 px-2 py-1 text-[11px] font-medium text-emerald-700">
                Live
              </span>
            </div>
            <div className="grid grid-cols-2 gap-4 text-left text-xs">
              <div className="rounded-xl bg-slate-50 p-4">
                <p className="text-[11px] font-medium uppercase tracking-wide text-slate-500">
                  Profile status
                </p>
                <p className="mt-2 text-sm font-semibold text-slate-900">
                  Verified
                </p>
              </div>
              <div className="rounded-xl bg-slate-50 p-4">
                <p className="text-[11px] font-medium uppercase tracking-wide text-slate-500">
                  Resumes stored
                </p>
                <p className="mt-2 text-sm font-semibold text-slate-900">
                  End‑to‑end encrypted
                </p>
              </div>
              <div className="col-span-2 rounded-xl bg-indigo-50 p-4">
                <p className="text-[11px] font-medium uppercase tracking-wide text-indigo-700">
                  Ready when you are
                </p>
                <p className="mt-2 text-xs text-indigo-900">
                  Create an account to unlock your secure job search dashboard.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default HomePage;

