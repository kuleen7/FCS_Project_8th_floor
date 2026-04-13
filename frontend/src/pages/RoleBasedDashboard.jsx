import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

function RoleBasedDashboard() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    // Get user data from localStorage
    const token = localStorage.getItem("token");
    const userData = localStorage.getItem("user");

    if (token && userData) {
      try {
        const parsedUser = JSON.parse(userData);
        setUser(parsedUser);
      } catch (error) {
        console.error("Error parsing user data:", error);
        navigate("/login");
      }
    } else {
      navigate("/login");
    }
    setLoading(false);
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    navigate("/login");
  };

  const handleNavigation = (path) => {
    navigate(path);
  };

  const roleLabel =
    user?.role === "recruiter" ? "Recruiter" : user?.role === "admin" ? "Admin" : "Job Seeker";
  const roleTone =
    user?.role === "recruiter"
      ? "from-blue-500 to-indigo-600"
      : user?.role === "admin"
      ? "from-violet-500 to-purple-600"
      : "from-emerald-500 to-teal-600";

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
          <p className="mt-4 text-slate-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  // Role-based dashboard content
  const renderDashboard = () => {
    switch (user.role) {
      case "user":
        return (
          <div className="p-6">
            <h1 className="text-2xl font-semibold text-slate-900 mb-6">Job Seeker Dashboard</h1>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-medium text-slate-900 mb-4">My Profile</h2>
                <p className="text-slate-600">Manage your profile and resume</p>
                <button
                  onClick={() => handleNavigation("/profile")}
                  className="mt-4 w-full bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"
                >
                  Edit Profile
                </button>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-medium text-slate-900 mb-4">Job Search</h2>
                <p className="text-slate-600">Find and apply for jobs</p>
                <button
                  onClick={() => handleNavigation("/jobs")}
                  className="mt-4 w-full bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"
                >
                  Search Jobs
                </button>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-medium text-slate-900 mb-4">My Applications</h2>
                <p className="text-slate-600">Track your job applications</p>
                <button
                  onClick={() => handleNavigation("/applications")}
                  className="mt-4 w-full bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"
                >
                  View Applications
                </button>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-medium text-slate-900 mb-4">Messages</h2>
                <p className="text-slate-600">Communicate with recruiters and teams</p>
                <button
                  onClick={() => handleNavigation("/messages")}
                  className="mt-4 w-full bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"
                >
                  View Messages
                </button>
              </div>
            </div>
          </div>
        );

      case "recruiter":
        return (
          <div className="p-6">
            <h1 className="text-2xl font-semibold text-slate-900 mb-6">Recruiter Dashboard</h1>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-medium text-slate-900 mb-4">Company Management</h2>
                <p className="text-slate-600">Manage your company page</p>
                <button
                  onClick={() => handleNavigation("/company")}
                  className="mt-4 w-full bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"
                >
                  Manage Company
                </button>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-medium text-slate-900 mb-4">Job Postings</h2>
                <p className="text-slate-600">Post and manage job listings</p>
                <button
                  onClick={() => handleNavigation("/jobs")}
                  className="mt-4 w-full bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"
                >
                  Manage Jobs
                </button>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-medium text-slate-900 mb-4">Applicants</h2>
                <p className="text-slate-600">Review job applications</p>
                <button
                  onClick={() => handleNavigation("/applications")}
                  className="mt-4 w-full bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"
                >
                  View Applicants
                </button>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-medium text-slate-900 mb-4">Messages</h2>
                <p className="text-slate-600">Communicate with candidates and team</p>
                <button
                  onClick={() => handleNavigation("/messages")}
                  className="mt-4 w-full bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"
                >
                  View Messages
                </button>
              </div>
            </div>
          </div>
        );

      case "admin":
        return (
          <div className="p-6">
            <h1 className="text-2xl font-semibold text-slate-900 mb-6">Platform Admin Dashboard</h1>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-medium text-slate-900 mb-4">User Management</h2>
                <p className="text-slate-600">Manage platform users</p>
                <button
                  onClick={() => handleNavigation("/admin/users")}
                  className="mt-4 w-full bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"
                >
                  Manage Users
                </button>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-medium text-slate-900 mb-4">System Monitoring</h2>
                <p className="text-slate-600">View system status and logs</p>
                <button
                  onClick={() => handleNavigation("/admin/system")}
                  className="mt-4 w-full bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"
                >
                  System Logs
                </button>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-medium text-slate-900 mb-4">Audit Logs</h2>
                <p className="text-slate-600">View tamper-evident audit logs</p>
                <button
                  onClick={() => handleNavigation("/admin/audit")}
                  className="mt-4 w-full bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"
                >
                  View Audit Logs
                </button>
              </div>
            </div>
          </div>
        );

      default:
        return (
          <div className="p-6">
            <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
              <h2 className="text-lg font-medium text-red-800 mb-2">Unknown Role</h2>
              <p className="text-red-600">Your user role ({user.role}) is not recognized.</p>
              <p className="text-red-600">Please contact support for assistance.</p>
            </div>
          </div>
        );
    }
  };

  return (
    <div className="space-y-6">
      <section className={`rounded-2xl bg-gradient-to-r ${roleTone} p-6 text-white shadow-lg`}>
        <p className="text-xs uppercase tracking-widest text-white/80">{roleLabel} Workspace</p>
        <h1 className="mt-2 text-2xl font-semibold">
          Welcome, {user.first_name || "User"} {user.last_name || ""}
        </h1>
        <p className="mt-2 text-sm text-white/90">
          Your dashboard is tailored to your role with secure actions and audited workflows.
        </p>
        <button
          onClick={handleLogout}
          className="mt-4 rounded-lg bg-white/20 px-4 py-2 text-sm font-medium hover:bg-white/30"
        >
          Logout
        </button>
      </section>
      <main>{renderDashboard()}</main>
    </div>
  );
}

export default RoleBasedDashboard;
