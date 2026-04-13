import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import api, { aprilAPI } from "../services/api";

function downloadFile(filename, content, mimeType) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  document.body.removeChild(anchor);
  URL.revokeObjectURL(url);
}

function AdminAuditPage() {
  const navigate = useNavigate();
  const [auditLogs, setAuditLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState("all");
  const [searchTerm, setSearchTerm] = useState("");
  const [integrity, setIntegrity] = useState(null);
  const [chainCheck, setChainCheck] = useState(null);

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

    const loadData = async () => {
      setLoading(true);
      setError("");
      try {
        const [logsRes, integrityRes, chainRes] = await Promise.all([
          api.get("/audit/logs?limit=100"),
          api.get("/audit/integrity"),
          aprilAPI.verifyChain(),
        ]);

        setAuditLogs(Array.isArray(logsRes.data?.logs) ? logsRes.data.logs : []);
        setIntegrity(integrityRes.data || null);
        setChainCheck(chainRes.data || null);
      } catch (err) {
        if (err?.response?.status === 422) {
          try {
            const logsRes = await api.get("/audit/logs?limit=50");
            setAuditLogs(Array.isArray(logsRes.data?.logs) ? logsRes.data.logs : []);
            setError("");
            setLoading(false);
            return;
          } catch (_fallbackErr) {
            // continue to normal error handler
          }
        }
        const normalizeError = (value) => {
          if (!value) return "";
          if (typeof value === "string") return value;
          if (Array.isArray(value)) {
            return value
              .map((item) => (typeof item === "string" ? item : JSON.stringify(item)))
              .join(" | ");
          }
          try {
            return JSON.stringify(value);
          } catch (_jsonErr) {
            return String(value);
          }
        };
        const message = normalizeError(
          err?.response?.data?.detail ||
            err?.response?.data?.message ||
            err?.message ||
            "Failed to load audit data"
        );
        setError(message);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [navigate]);

  const filteredLogs = useMemo(() => {
    return auditLogs.filter((log) => {
      const action = (log.action || log.action_type || "").toString();
      const details = (log.details || "").toString();
      const userText = (
        log.user_email ||
        log.userEmail ||
        log.user_id ||
        log.userId ||
        "system"
      ).toString();
      const matchesFilter = filter === "all" || action === filter;
      const lowered = searchTerm.toLowerCase();
      const matchesSearch =
        !lowered ||
        action.toLowerCase().includes(lowered) ||
        details.toLowerCase().includes(lowered) ||
        userText.toLowerCase().includes(lowered);
      return matchesFilter && matchesSearch;
    });
  }, [auditLogs, filter, searchTerm]);

  const actions = useMemo(() => {
    const unique = new Set();
    auditLogs.forEach((log) => {
      const action = (log.action || log.action_type || "").toString().trim();
      if (action) unique.add(action);
    });
    return Array.from(unique).sort();
  }, [auditLogs]);

  const exportJson = () => {
    const payload = {
      exported_at: new Date().toISOString(),
      integrity,
      chainCheck,
      logs: filteredLogs,
    };
    downloadFile(
      `audit-logs-${Date.now()}.json`,
      JSON.stringify(payload, null, 2),
      "application/json"
    );
  };

  const exportCsv = () => {
    const rows = [
      ["timestamp", "user", "action", "status", "ip_address", "details"],
      ...filteredLogs.map((log) => [
        log.timestamp || log.created_at || "",
        log.user_email || log.userEmail || log.user_id || log.userId || "system",
        log.action || log.action_type || "",
        log.status || log.success || "",
        log.ip_address || log.ipAddress || "",
        (log.details || "").toString().replace(/\n/g, " "),
      ]),
    ];
    const csv = rows
      .map((row) => row.map((value) => `"${String(value).replace(/"/g, '""')}"`).join(","))
      .join("\n");
    downloadFile(`audit-logs-${Date.now()}.csv`, csv, "text/csv;charset=utf-8;");
  };

  const getBadgeClass = (value) => {
    const normalized = String(value || "").toLowerCase();
    if (normalized.includes("fail") || normalized.includes("error")) {
      return "bg-rose-100 text-rose-700";
    }
    if (normalized.includes("success") || normalized === "true") {
      return "bg-emerald-100 text-emerald-700";
    }
    return "bg-slate-100 text-slate-700";
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="mx-auto h-12 w-12 animate-spin rounded-full border-b-2 border-indigo-600" />
          <p className="mt-4 text-slate-600">Loading real audit logs...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-indigo-50/40">
      <div className="border-b border-slate-200 bg-white/90 backdrop-blur">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <h1 className="text-xl font-semibold text-slate-900">Audit Logs</h1>
          <button
            onClick={() => navigate("/dashboard")}
            className="rounded-lg border border-slate-200 px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-50"
          >
            Back to Dashboard
          </button>
        </div>
      </div>

      <main className="mx-auto max-w-7xl space-y-5 px-4 py-6 sm:px-6 lg:px-8">
        {error && (
          <div className="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
            {error}
          </div>
        )}

        <div className="grid gap-4 md:grid-cols-3">
          <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
            <p className="text-sm text-slate-500">Total Logs</p>
            <p className="mt-1 text-2xl font-semibold text-slate-900">{auditLogs.length}</p>
          </div>
          <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
            <p className="text-sm text-slate-500">Hash Chain Integrity</p>
            <p className={`mt-1 inline-flex rounded-full px-2.5 py-1 text-xs font-medium ${getBadgeClass(integrity?.is_valid)}`}>
              {integrity?.is_valid ? "VALID" : "CHECK NEEDED"}
            </p>
          </div>
          <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
            <p className="text-sm text-slate-500">Blockchain Verification</p>
            <p className={`mt-1 inline-flex rounded-full px-2.5 py-1 text-xs font-medium ${getBadgeClass(chainCheck?.valid ?? chainCheck?.is_valid)}`}>
              {chainCheck?.valid ?? chainCheck?.is_valid ? "VALID" : "CHECK NEEDED"}
            </p>
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
          <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
            <div className="flex flex-col gap-3 sm:flex-row">
              <div>
                <label className="mb-1 block text-xs font-medium text-slate-600">Action</label>
                <select
                  value={filter}
                  onChange={(e) => setFilter(e.target.value)}
                  className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
                >
                  <option value="all">All Actions</option>
                  {actions.map((action) => (
                    <option key={action} value={action}>
                      {action}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="mb-1 block text-xs font-medium text-slate-600">Search</label>
                <input
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="action / email / details"
                  className="w-72 rounded-lg border border-slate-300 px-3 py-2 text-sm"
                />
              </div>
            </div>
            <div className="text-sm text-slate-600">{filteredLogs.length} logs found</div>
          </div>
        </div>

        <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">Timestamp</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">User</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">Action</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">Status</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">IP</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 bg-white">
                {filteredLogs.map((log, index) => {
                  const ts = log.timestamp || log.created_at;
                  const user = log.user_email || log.userEmail || log.user_id || log.userId || "system";
                  const action = log.action || log.action_type || "unknown";
                  const statusValue = String(log.status || log.success || "N/A");
                  return (
                    <tr key={log.id || `${action}-${index}`}>
                      <td className="whitespace-nowrap px-4 py-3 text-sm text-slate-600">
                        {ts ? new Date(ts).toLocaleString() : "-"}
                      </td>
                      <td className="whitespace-nowrap px-4 py-3 text-sm text-slate-800">{user}</td>
                      <td className="px-4 py-3 text-sm text-slate-700">{action}</td>
                      <td className="px-4 py-3 text-sm">
                        <span className={`rounded-full px-2 py-1 text-xs font-medium ${getBadgeClass(statusValue)}`}>
                          {statusValue}
                        </span>
                      </td>
                      <td className="whitespace-nowrap px-4 py-3 text-sm text-slate-600">
                        {log.ip_address || log.ipAddress || "-"}
                      </td>
                      <td className="max-w-md px-4 py-3 text-sm text-slate-600">
                        <span className="line-clamp-2">{log.details || "-"}</span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          {filteredLogs.length === 0 && (
            <div className="px-4 py-8 text-center text-sm text-slate-500">
              No logs match this filter.
            </div>
          )}
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={exportCsv}
            className="rounded-lg border border-slate-300 px-4 py-2 text-sm text-slate-700 hover:bg-slate-50"
          >
            Export CSV
          </button>
          <button
            onClick={exportJson}
            className="rounded-lg border border-slate-300 px-4 py-2 text-sm text-slate-700 hover:bg-slate-50"
          >
            Export JSON
          </button>
          <button
            onClick={() => window.print()}
            className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
          >
            Generate Report
          </button>
        </div>
      </main>
    </div>
  );
}

export default AdminAuditPage;
