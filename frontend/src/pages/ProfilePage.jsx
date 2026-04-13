import { useEffect, useState } from "react";
import { authAPI, userAPI } from "../services/api";
import Loader from "../components/Loader";

function ProfilePage() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [form, setForm] = useState({
    name: "",
    email: "",
    mobile: "",
  });

  useEffect(() => {
    let isMounted = true;

    const fetchProfile = async () => {
      try {
        const res = await authAPI.getCurrentUser();
        if (!isMounted) return;
        const data = res.data || {};
        setForm({
          name: data.name || "",
          email: data.email || "",
          mobile: data.mobile || "",
        });
      } catch (err) {
        if (!isMounted) return;
        const message =
          err.response?.data?.message ||
          err.response?.data?.error ||
          "Unable to load profile.";
        setError(message);
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchProfile();

    return () => {
      isMounted = false;
    };
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    setSaving(true);

    try {
      await userAPI.updateProfile(form);
      setSuccess("Profile updated successfully.");
    } catch (err) {
      const message =
        err.response?.data?.message ||
        err.response?.data?.error ||
        "Unable to update profile.";
      setError(message);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <Loader />;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">Profile</h1>
        <p className="mt-1 text-sm text-slate-500">
          Manage the information employers see when you apply.
        </p>
      </div>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          {error}
        </div>
      )}
      {success && (
        <div className="rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-700">
          {success}
        </div>
      )}

      <form
        onSubmit={handleSubmit}
        className="space-y-4 rounded-xl bg-slate-50 p-6 shadow-md"
      >
        <div className="grid gap-4 md:grid-cols-2">
          <div className="space-y-1">
            <label
              htmlFor="name"
              className="text-sm font-medium text-slate-700"
            >
              Full name
            </label>
            <input
              id="name"
              name="name"
              type="text"
              className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-900 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              value={form.name}
              onChange={handleChange}
            />
          </div>

          <div className="space-y-1">
            <label
              htmlFor="email"
              className="text-sm font-medium text-slate-700"
            >
              Email
            </label>
            <input
              id="email"
              name="email"
              type="email"
              disabled
              className="w-full cursor-not-allowed rounded-lg border border-slate-200 bg-slate-100 px-3 py-2 text-sm text-slate-500 shadow-sm"
              value={form.email}
              onChange={handleChange}
            />
          </div>

          <div className="space-y-1">
            <label
              htmlFor="mobile"
              className="text-sm font-medium text-slate-700"
            >
              Mobile
            </label>
            <input
              id="mobile"
              name="mobile"
              type="tel"
              className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-900 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              value={form.mobile}
              onChange={handleChange}
            />
          </div>
        </div>

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={saving}
            className="inline-flex items-center justify-center rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-medium text-white shadow-md transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {saving ? "Saving changes..." : "Save changes"}
          </button>
        </div>
      </form>
    </div>
  );
}

export default ProfilePage;

