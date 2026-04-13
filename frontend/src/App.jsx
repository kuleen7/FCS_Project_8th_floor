import { BrowserRouter, Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage.jsx";
import LoginPage from "./pages/LoginPage.jsx";
import RegisterPage from "./pages/RegisterPage.jsx";
import OTPVerificationPage from "./pages/OTPVerificationPage.jsx";
import RoleBasedDashboard from "./pages/RoleBasedDashboard.jsx";
import EnhancedProfilePage from "./pages/EnhancedProfilePage.jsx";
import ApplicationStatusPage from "./pages/ApplicationStatusPage.jsx";
import GroupMessagingPage from "./pages/GroupMessagingPage.jsx";
import EnhancedResumePage from "./pages/EnhancedResumePage.jsx";
import CompanyManagementPage from "./pages/CompanyManagementPage.jsx";
import JobManagementPage from "./pages/JobManagementPage.jsx";
import JobSearchPage from "./pages/JobSearchPage.jsx";
import AdminUserManagementPage from "./pages/AdminUserManagementPage.jsx";
import AdminSystemPage from "./pages/AdminSystemPage.jsx";
import AdminAuditPage from "./pages/AdminAuditPage.jsx";
import ProtectedRoute from "./components/ProtectedRoute";

function NotFoundPage() {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center gap-4 text-center">
      <h1 className="text-3xl font-semibold text-slate-900">Page not found</h1>
      <p className="max-w-md text-sm text-slate-500">
        The page you are looking for doesn&apos;t exist or has been moved.
      </p>
      <a
        href="/"
        className="mt-2 inline-flex items-center justify-center rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-indigo-700"
      >
        Back to home
      </a>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public */}
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/verify-otp" element={<OTPVerificationPage />} />

        {/* Protected */}
        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard" element={<RoleBasedDashboard />} />
          <Route path="/profile" element={<EnhancedProfilePage />} />
          <Route path="/applications" element={<ApplicationStatusPage />} />
          <Route path="/messages" element={<GroupMessagingPage />} />
          <Route path="/resumes" element={<EnhancedResumePage />} />
          <Route path="/company" element={<CompanyManagementPage />} />
          <Route path="/jobs" element={<JobManagementPage />} />
          <Route path="/jobs/search" element={<JobSearchPage />} />
          <Route path="/admin/users" element={<AdminUserManagementPage />} />
          <Route path="/admin/system" element={<AdminSystemPage />} />
          <Route path="/admin/audit" element={<AdminAuditPage />} />
        </Route>

        {/* 404 */}
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;

