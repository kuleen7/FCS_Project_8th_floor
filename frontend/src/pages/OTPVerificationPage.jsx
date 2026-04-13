import { useState, useEffect } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { authAPI } from "../services/api";

function OTPVerificationPage() {
  const [otpCode, setOtpCode] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [email, setEmail] = useState("");

  const navigate = useNavigate();
  const location = useLocation();

  // Get email from registration state or query params
  useEffect(() => {
    const stateEmail = location.state?.email;
    const paramsEmail = new URLSearchParams(location.search).get("email");
    const emailToUse = stateEmail || paramsEmail;

    if (emailToUse) {
      setEmail(emailToUse);
    } else {
      // If no email, redirect to register
      navigate("/register");
    }
  }, [location.state, location.search, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    setIsSubmitting(true);

    try {
      const response = await authAPI.verifyEmail({
        email: email,
        otp_code: otpCode
      });

      setSuccess("Email verified successfully! Redirecting to login...");

      // Redirect to login after 2 seconds
      setTimeout(() => {
        navigate("/login", {
          state: { message: "Email verified! You can now login." }
        });
      }, 2000);

    } catch (err) {
      const message =
        err.response?.data?.detail ||
        err.response?.data?.message ||
        "Invalid OTP code. Please try again.";
      setError(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleResendOTP = async () => {
    setError("");
    setSuccess("");

    try {
      const response = await authAPI.resendOTP({ email });
      setSuccess("OTP resent successfully! Check your email.");
    } catch (err) {
      const message =
        err.response?.data?.detail ||
        err.response?.data?.message ||
        "Failed to resend OTP. Please try again.";
      setError(message);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
      <div className="mx-auto w-full max-w-md rounded-2xl bg-white p-8 shadow-md">
        <div className="mb-6 space-y-1 text-center">
          <h1 className="text-2xl font-semibold text-slate-900">
            Verify Your Email
          </h1>
          <p className="text-sm text-slate-500">
            Enter the 6-digit code sent to {email}
          </p>
        </div>

        {error && (
          <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
            {error}
          </div>
        )}

        {success && (
          <div className="mb-4 rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-700">
            {success}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1">
            <label
              htmlFor="otpCode"
              className="text-sm font-medium text-slate-700"
            >
              OTP Code
            </label>
            <input
              id="otpCode"
              type="text"
              required
              maxLength="6"
              minLength="6"
              pattern="[0-9]{6}"
              placeholder="Enter 6-digit code"
              className="w-full rounded-lg border border-slate-200 px-3 py-2 text-center text-lg font-mono text-slate-900 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              value={otpCode}
              onChange={(e) => setOtpCode(e.target.value.replace(/\D/g, ""))}
            />
          </div>

          <button
            type="submit"
            disabled={isSubmitting || otpCode.length !== 6}
            className="mt-2 inline-flex w-full items-center justify-center rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-medium text-white shadow-md transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isSubmitting ? "Verifying..." : "Verify Email"}
          </button>
        </form>

        <div className="mt-6 text-center">
          <button
            onClick={handleResendOTP}
            className="text-sm text-indigo-600 hover:text-indigo-700"
          >
            Didn't receive the code? Resend OTP
          </button>
        </div>

        <div className="mt-4 text-center">
          <p className="text-xs text-slate-500">
            Wrong email?{" "}
            <Link
              to="/register"
              className="font-medium text-indigo-600 hover:text-indigo-700"
            >
              Register again
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}

export default OTPVerificationPage;
