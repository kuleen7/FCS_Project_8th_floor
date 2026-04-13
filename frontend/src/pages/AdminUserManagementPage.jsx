import { useEffect, useMemo, useState } from "react";
import { adminAPI, buildHighRiskHeaders } from "../services/api";

function AdminUserManagementPage() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [error, setError] = useState("");
  const [busyUser, setBusyUser] = useState(null);

  const loadUsers = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await adminAPI.getUsers();
      setUsers(res.data || []);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load users");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  const visibleUsers = useMemo(() => {
    const term = search.toLowerCase();
    return users.filter(
      (u) =>
        `${u.first_name || ""} ${u.last_name || ""}`.toLowerCase().includes(term) ||
        (u.email || "").toLowerCase().includes(term)
    );
  }, [users, search]);

  const withHighRisk = async (userId, actionName, callback) => {
    try {
      setBusyUser(userId);
      const headers = await buildHighRiskHeaders(actionName);
      await callback(headers);
      await loadUsers();
      window.alert("Admin high-risk action completed.");
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "High-risk action failed");
    } finally {
      setBusyUser(null);
    }
  };

  if (loading) return <div className="p-4">Loading admin users...</div>;

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-semibold">Admin User Management (April Secured)</h2>
      <p className="text-sm text-slate-600">
        Suspend/reactivate/delete actions require PKI signing and virtual keyboard OTP.
      </p>
      <input
        className="w-full rounded border px-3 py-2"
        placeholder="Search users by name or email"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />
      {error ? <p className="text-sm text-red-600">{error}</p> : null}

      <div className="space-y-2">
        {visibleUsers.map((user) => (
          <div key={user.id} className="rounded border p-3">
            <p className="font-medium">
              {user.first_name} {user.last_name} - {user.email}
            </p>
            <p className="text-sm text-slate-600">
              role: {user.role} | active: {String(user.is_active)} | verified: {String(user.is_verified)}
            </p>
            <div className="mt-2 flex gap-2">
              {user.is_active ? (
                <button
                  disabled={busyUser === user.id}
                  className="rounded border px-3 py-1"
                  onClick={() =>
                    withHighRisk(user.id, "admin.user.suspend", (headers) =>
                      adminAPI.suspendUser(user.id, headers)
                    )
                  }
                >
                  Suspend (Secure)
                </button>
              ) : (
                <button
                  disabled={busyUser === user.id}
                  className="rounded border px-3 py-1"
                  onClick={() =>
                    withHighRisk(user.id, "admin.user.reactivate", (headers) =>
                      adminAPI.reactivateUser(user.id, headers)
                    )
                  }
                >
                  Reactivate (Secure)
                </button>
              )}
              <button
                disabled={busyUser === user.id}
                className="rounded border px-3 py-1 text-red-600"
                onClick={() => {
                  if (!window.confirm("Delete this user account?")) return;
                  withHighRisk(user.id, "admin.user.delete", (headers) => adminAPI.deleteUser(user.id, headers));
                }}
              >
                Delete (Secure)
              </button>
            </div>
          </div>
        ))}
        {visibleUsers.length === 0 ? <p className="text-sm text-slate-500">No users found.</p> : null}
      </div>
    </div>
  );
}

export default AdminUserManagementPage;
