import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { authAPI } from "../services/api";

function RegisterPage() {
  const [email, setEmail] = useState("");
  const [mobile, setMobile] = useState("");
  const [password, setPassword] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [role, setRole] = useState("user");
  const [companyName, setCompanyName] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    setIsSubmitting(true);

    try {
      const registrationData = {
        email,
        password,
        mobile,
        first_name: firstName,
        last_name: lastName,
        role: role
      };

      if (role === "recruiter" && companyName) {
        registrationData.company_name = companyName;
      }

      await authAPI.register(registrationData);
      setSuccess("Account created successfully! Please check your email for verification code.");

      // Redirect to OTP verification page with email
      setTimeout(() => {
        navigate("/verify-otp", {
          state: { email: email }
        });
      }, 1500);
    } catch (err) {
      const detail =
        err.response?.data?.detail ||
        err.response?.data?.message ||
        err.response?.data?.error ||
        "";
      let message = "Unable to register. Please check your details.";
      if (typeof detail === "string" && detail.trim()) {
        message = detail;
      }
      if (message.toLowerCase().includes("already")) {
        if (message.toLowerCase().includes("mobile")) {
          message = "Mobile number already exists. Please use another number.";
        } else if (message.toLowerCase().includes("email")) {
          message = "Email already exists. Please use another email.";
        }
      }
      if (message.toLowerCase().includes("password")) {
        message =
          "Password must be 8+ characters and include uppercase, lowercase, number, and special character.";
      }
      setError(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
      <div className="mx-auto w-full max-w-md rounded-2xl bg-white p-8 shadow-md">
        <div className="mb-6 space-y-1 text-center">
          <h1 className="text-2xl font-semibold text-slate-900">
            Create your account
          </h1>
          <p className="text-sm text-slate-500">
            Start your secure job search in minutes.
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
              htmlFor="role"
              className="text-sm font-medium text-slate-700"
            >
              I am a
            </label>
            <select
              id="role"
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-900 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="user">Job Seeker</option>
              <option value="recruiter">Recruiter / Company Admin</option>
              <option value="admin">Platform Admin</option>
            </select>
          </div>

          {role === "recruiter" && (
            <div className="space-y-1">
              <label
                htmlFor="companyName"
                className="text-sm font-medium text-slate-700"
              >
                Company Name
              </label>
              <input
                id="companyName"
                type="text"
                required={role === "recruiter"}
                autoComplete="organization"
                placeholder="Enter your company name"
                className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-900 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
              />
            </div>
          )}

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
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <label
                htmlFor="firstName"
                className="text-sm font-medium text-slate-700"
              >
                First Name
              </label>
              <input
                id="firstName"
                type="text"
                required
                autoComplete="given-name"
                className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-900 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
              />
            </div>

            <div className="space-y-1">
              <label
                htmlFor="lastName"
                className="text-sm font-medium text-slate-700"
              >
                Last Name
              </label>
              <input
                id="lastName"
                type="text"
                required
                autoComplete="family-name"
                className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-900 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
              />
            </div>
          </div>

          <div className="space-y-1">
            <label
              htmlFor="mobile"
              className="text-sm font-medium text-slate-700"
            >
              Mobile (10-15 digits)
            </label>
            <input
              id="mobile"
              type="tel"
              required
              minLength="10"
              maxLength="15"
              autoComplete="tel"
              className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-900 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              value={mobile}
              onChange={(e) => setMobile(e.target.value)}
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
              autoComplete="new-password"
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
            {isSubmitting ? "Creating account..." : "Create account"}
          </button>
        </form>

        <p className="mt-6 text-center text-xs text-slate-500">
          Already have an account?{" "}
          <Link
            to="/login"
            className="font-medium text-indigo-600 hover:text-indigo-700"
          >
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}

export default RegisterPage;

