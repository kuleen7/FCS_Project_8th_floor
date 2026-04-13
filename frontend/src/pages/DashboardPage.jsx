import { useEffect, useState } from "react";
import { authAPI, userAPI } from "../services/api";
import Loader from "../components/Loader";

function DashboardPage() {
  const [profile, setProfile] = useState(null);
  const [resumes, setResumes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let isMounted = true;
    const fetchData = async () => {
      try {
        const [meRes, resumeRes] = await Promise.all([
          authAPI.getCurrentUser(),
          userAPI.listResumes(),
        ]);
        if (!isMounted) return;
        setProfile(meRes.data || null);
        setResumes(resumeRes.data || []);
      } catch (err) {
        if (!isMounted) return;
        const message =
          err.response?.data?.message ||
          err.response?.data?.error ||
          "Unable to load dashboard data.";
        setError(message);
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchData();

    return () => {
      isMounted = false;
    };
  }, []);

  if (loading) {
    return <Loader />;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">
          Welcome back{profile?.name ? `, ${profile.name}` : ""} 👋
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          Here&apos;s a quick overview of your secure job search workspace.
        </p>
      </div>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          {error}
        </div>
      )}

      <div className="grid gap-4 md:grid-cols-3">
        <div className="rounded-xl bg-indigo-50 p-6 shadow-md">
          <p className="text-xs font-medium uppercase tracking-wide text-indigo-700">
            Profile status
          </p>
          <p className="mt-3 text-2xl font-semibold text-slate-900">
            {profile?.status || "Active"}
          </p>
          <p className="mt-1 text-xs text-slate-600">
            Keep your profile up to date to stand out to employers.
          </p>
        </div>

        <div className="rounded-xl bg-white p-6 shadow-md">
          <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
            Resumes on file
          </p>
          <p className="mt-3 text-2xl font-semibold text-slate-900">
            {Array.isArray(resumes) ? resumes.length : 0}
          </p>
          <p className="mt-1 text-xs text-slate-600">
            Upload tailored resumes for different roles and industries.
          </p>
        </div>

        <div className="rounded-xl bg-white p-6 shadow-md">
          <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
            Account type
          </p>
          <p className="mt-3 text-2xl font-semibold text-slate-900">
            {profile?.accountType || profile?.role || "Candidate"}
          </p>
          <p className="mt-1 text-xs text-slate-600">
            Upgrade through your organization or contact support to change.
          </p>
        </div>
      </div>
    </div>
  );
}

export default DashboardPage;

