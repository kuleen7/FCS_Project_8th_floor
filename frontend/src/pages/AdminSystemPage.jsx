import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { adminAPI, applicationsAPI, auditAPI, jobsAPI } from "../services/api";

function AdminSystemPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [stats, setStats] = useState(null);

  const loadSystemData = async () => {
    setLoading(true);
    setError("");
    try {
      const [adminStatsRes, jobsStatsRes, appStatsRes, auditSummaryRes] = await Promise.all([
        adminAPI.getStats(),
        jobsAPI.statistics(),
        applicationsAPI.statistics(),
        auditAPI.systemSummary(7),
      ]);

      const adminStats = adminStatsRes.data || {};
      const jobsStats = jobsStatsRes.data || {};
      const appStats = appStatsRes.data || {};
      const auditSummary = auditSummaryRes.data || {};

      const messageActions = Number(auditSummary.actions_by_type?.MESSAGE_SEND || 0);

      setStats({
        users: {
          total: Number(adminStats.total_users || 0),
          active: Number(adminStats.active_users || 0),
          verified: Number(adminStats.verified_users || 0),
          suspended: Number(adminStats.suspended_users || 0),
          byRole: {
            user: Number(adminStats.users_by_role?.users || 0),
            recruiter: Number(adminStats.users_by_role?.recruiters || 0),
            admin: Number(adminStats.users_by_role?.admins || 0),
          },
        },
        jobs: {
          total: Number(jobsStats.total_jobs || 0),
          active: Number(jobsStats.active_jobs || 0),
          featured: Number(jobsStats.featured_jobs || 0),
          closed: Math.max(0, Number(jobsStats.total_jobs || 0) - Number(jobsStats.active_jobs || 0)),
        },
        applications: {
          total: Number(appStats.total_applications || 0),
          shortlisted: Number(appStats.shortlisted_count || 0),
          statusDistribution: appStats.status_distribution || {},
        },
        activity: {
          periodDays: Number(auditSummary.period_days || 7),
          totalActions: Number(auditSummary.total_actions || 0),
          activeUsers: Number(auditSummary.active_users || 0),
          messageActions,
        },
        system: {
          version: "1.0.0",
          lastUpdatedAt: new Date().toISOString(),
        },
      });
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to load system monitoring data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const userData = localStorage.getItem("user");
    if (!userData) {
      navigate("/login");
      return;
    }
    const user = JSON.parse(userData);
    if (user.role !== "admin") {
      navigate("/dashboard");
      return;
    }
    loadSystemData();
  }, [navigate]);

  const applicationStatusRows = useMemo(() => {
    if (!stats?.applications?.statusDistribution) return [];
    return Object.entries(stats.applications.statusDistribution).map(([status, count]) => ({
      status,
      count: Number(count || 0),
    }));
  }, [stats]);

  if (loading) {
    return <div className="p-4 text-sm text-slate-600">Loading real-time system data...</div>;
  }

  if (!stats) {
    return <div className="p-4 text-sm text-rose-600">{error || "No system data available."}</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h1 className="text-2xl font-semibold text-slate-900">System Monitoring</h1>
        <div className="flex gap-2">
          <button onClick={() => navigate("/dashboard")} className="rounded border px-3 py-2 text-sm">
            Back to Dashboard
          </button>
          <button onClick={loadSystemData} className="rounded border px-3 py-2 text-sm">
            Refresh Live Data
          </button>
        </div>
      </div>

      {error ? <p className="rounded border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">{error}</p> : null}

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-lg border bg-white p-4 shadow-sm">
          <p className="text-sm text-slate-500">Total Users</p>
          <p className="mt-1 text-2xl font-semibold text-indigo-600">{stats.users.total.toLocaleString()}</p>
          <p className="text-xs text-slate-500">{stats.users.active.toLocaleString()} active</p>
        </div>
        <div className="rounded-lg border bg-white p-4 shadow-sm">
          <p className="text-sm text-slate-500">Active Jobs</p>
          <p className="mt-1 text-2xl font-semibold text-emerald-600">{stats.jobs.active.toLocaleString()}</p>
          <p className="text-xs text-slate-500">of {stats.jobs.total.toLocaleString()} total</p>
        </div>
        <div className="rounded-lg border bg-white p-4 shadow-sm">
          <p className="text-sm text-slate-500">Applications</p>
          <p className="mt-1 text-2xl font-semibold text-purple-600">{stats.applications.total.toLocaleString()}</p>
          <p className="text-xs text-slate-500">{stats.applications.shortlisted.toLocaleString()} shortlisted</p>
        </div>
        <div className="rounded-lg border bg-white p-4 shadow-sm">
          <p className="text-sm text-slate-500">Message Sends (7d)</p>
          <p className="mt-1 text-2xl font-semibold text-blue-600">{stats.activity.messageActions.toLocaleString()}</p>
          <p className="text-xs text-slate-500">{stats.activity.totalActions.toLocaleString()} total actions / {stats.activity.periodDays}d</p>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded-lg border bg-white p-4 shadow-sm">
          <h2 className="mb-3 text-lg font-medium text-slate-900">User Statistics</h2>
          <div className="space-y-2 text-sm">
            <p>Total: {stats.users.total.toLocaleString()}</p>
            <p>Active: {stats.users.active.toLocaleString()}</p>
            <p>Verified: {stats.users.verified.toLocaleString()}</p>
            <p>Suspended: {stats.users.suspended.toLocaleString()}</p>
            <div className="border-t pt-2 text-xs text-slate-600">
              <p>Job Seekers: {stats.users.byRole.user.toLocaleString()}</p>
              <p>Recruiters: {stats.users.byRole.recruiter.toLocaleString()}</p>
              <p>Admins: {stats.users.byRole.admin.toLocaleString()}</p>
            </div>
          </div>
        </div>

        <div className="rounded-lg border bg-white p-4 shadow-sm">
          <h2 className="mb-3 text-lg font-medium text-slate-900">Application Status Distribution</h2>
          <div className="space-y-2 text-sm">
            {applicationStatusRows.length ? (
              applicationStatusRows.map((row) => (
                <div key={row.status} className="flex items-center justify-between">
                  <span>{row.status}</span>
                  <span>{row.count.toLocaleString()}</span>
                </div>
              ))
            ) : (
              <p className="text-slate-500">No application status data yet.</p>
            )}
          </div>
        </div>

        <div className="rounded-lg border bg-white p-4 shadow-sm">
          <h2 className="mb-3 text-lg font-medium text-slate-900">Job Statistics</h2>
          <div className="space-y-2 text-sm">
            <p>Total Jobs: {stats.jobs.total.toLocaleString()}</p>
            <p>Active Jobs: {stats.jobs.active.toLocaleString()}</p>
            <p>Closed/Inactive Jobs: {stats.jobs.closed.toLocaleString()}</p>
            <p>Featured Jobs: {stats.jobs.featured.toLocaleString()}</p>
          </div>
        </div>

        <div className="rounded-lg border bg-white p-4 shadow-sm">
          <h2 className="mb-3 text-lg font-medium text-slate-900">System Information</h2>
          <div className="space-y-2 text-sm">
            <p>Version: {stats.system.version}</p>
            <p>Active Users (Last {stats.activity.periodDays}d): {stats.activity.activeUsers.toLocaleString()}</p>
            <p>Total Actions (Last {stats.activity.periodDays}d): {stats.activity.totalActions.toLocaleString()}</p>
            <p>Last Refreshed: {new Date(stats.system.lastUpdatedAt).toLocaleString()}</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AdminSystemPage;
