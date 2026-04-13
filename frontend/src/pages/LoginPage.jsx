import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { authAPI } from "../services/api";

function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [totpCode, setTotpCode] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isRequestingReset, setIsRequestingReset] = useState(false);
  const [showResetForm, setShowResetForm] = useState(false);
  const [resetOtp, setResetOtp] = useState("");
  const [resetPassword, setResetPassword] = useState("");
  const [isResetting, setIsResetting] = useState(false);
  const [error, setError] = useState("");
  const [info, setInfo] = useState("");

  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from?.pathname || "/dashboard";

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setInfo("");
    setIsSubmitting(true);

    try {
      const payload = { email, password };
      if (totpCode.trim()) {
        payload.totp_code = totpCode.trim();
      }
      const response = await authAPI.login(payload);
      const data = response.data || {};
      if (data.token) {
        localStorage.setItem("token", data.token);
      }
      if (data.user) {
        localStorage.setItem("user", JSON.stringify(data.user));
      }
      navigate(from, { replace: true });
    } catch (err) {
      const message =
        err.response?.data?.detail ||
        err.response?.data?.message ||
        err.response?.data?.error ||
        "Unable to sign in. Please check your credentials.";
      setError(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleForgotPassword = async () => {
    setError("");
    setInfo("");
    if (!email.trim()) {
      setError("Enter your email first, then click Forgot password.");
      return;
    }
    setIsRequestingReset(true);
    try {
      await authAPI.requestPasswordResetOtp(email.trim());
      setInfo("Password reset OTP sent. Enter OTP and new password below.");
      setShowResetForm(true);
    } catch (err) {
      setError(err.response?.data?.detail || "Could not request password reset OTP.");
    } finally {
      setIsRequestingReset(false);
    }
  };

  const handleResetPassword = async (e) => {
    e.preventDefault();
    setError("");
    setInfo("");
    if (!email.trim() || !resetOtp.trim() || !resetPassword.trim()) {
      setError("Email, OTP, and new password are required.");
      return;
    }
    setIsResetting(true);
    try {
      await authAPI.resetPasswordWithOtp({
        email: email.trim(),
        otp_code: resetOtp.trim(),
        new_password: resetPassword,
      });
      setInfo("Password reset successful. You can sign in with the new password.");
      setShowResetForm(false);
      setResetOtp("");
      setResetPassword("");
    } catch (err) {
      setError(err.response?.data?.detail || "Could not reset password.");
    } finally {
      setIsResetting(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
      <div className="mx-auto w-full max-w-md rounded-2xl bg-white p-8 shadow-md">
        <div className="mb-6 space-y-1 text-center">
          <h1 className="text-2xl font-semibold text-slate-900">
            Sign in to your account
          </h1>
          <p className="text-sm text-slate-500">
            Access your secure job search dashboard.
          </p>
        </div>

        {error && (
          <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
            {error}
          </div>
        )}
        {info && (
          <div className="mb-4 rounded-lg border border-blue-200 bg-blue-50 px-3 py-2 text-sm text-blue-700">
            {info}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1">
            <label
              htmlFor="email"
              className="text-sm font-medium text-slate-700"
            >
              Email
            </label>
            <input
              id="email"
              type="email"
              required
              autoComplete="email"
              className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-900 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <div className="mt-1 text-right">
              <button
                type="button"
                onClick={handleForgotPassword}
                disabled={isRequestingReset}
                className="text-xs font-medium text-indigo-600 hover:text-indigo-700 disabled:opacity-60"
              >
                {isRequestingReset ? "Requesting..." : "Forgot password?"}
              </button>
            </div>
          </div>

          <div className="space-y-1">
            <label htmlFor="totpCode" className="text-sm font-medium text-slate-700">
              Authenticator Code (optional)
            </label>
            <input
              id="totpCode"
              type="text"
              inputMode="numeric"
              maxLength={6}
              placeholder="6-digit TOTP code"
              className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-900 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              value={totpCode}
              onChange={(e) => setTotpCode(e.target.value)}
            />
          </div>

          <div className="space-y-1">
            <label
              htmlFor="password"
              className="text-sm font-medium text-slate-700"
            >
              Password
            </label>
            <input
              id="password"
              type="password"
              required
              autoComplete="current-password"
              className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-900 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="mt-2 inline-flex w-full items-center justify-center rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-medium text-white shadow-md transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isSubmitting ? "Signing in..." : "Sign in"}
          </button>
        </form>

        {showResetForm && (
          <form onSubmit={handleResetPassword} className="mt-4 space-y-3 rounded-lg border border-indigo-200 bg-indigo-50 p-3">
            <p className="text-sm font-medium text-indigo-900">Complete password reset</p>
            <input
              type="text"
              value={resetOtp}
              onChange={(e) => setResetOtp(e.target.value)}
              placeholder="Enter OTP"
              className="w-full rounded border border-indigo-200 px-3 py-2 text-sm"
            />
            <input
              type="password"
              value={resetPassword}
              onChange={(e) => setResetPassword(e.target.value)}
              placeholder="Enter new password"
              className="w-full rounded border border-indigo-200 px-3 py-2 text-sm"
            />
            <button
              type="submit"
              disabled={isResetting}
              className="w-full rounded bg-indigo-600 px-3 py-2 text-sm font-medium text-white disabled:opacity-60"
            >
              {isResetting ? "Resetting..." : "Reset Password"}
            </button>
          </form>
        )}

        <p className="mt-6 text-center text-xs text-slate-500">
          Don&apos;t have an account?{" "}
          <Link
            to="/register"
            className="font-medium text-indigo-600 hover:text-indigo-700"
          >
            Create one
          </Link>
        </p>
      </div>
    </div>
  );
}

export default LoginPage;

