import { useEffect, useState } from "react";
import { userAPI } from "../services/api";
import Loader from "../components/Loader";

function ResumePage() {
  const [resumes, setResumes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const loadResumes = async () => {
    setError("");
    try {
      const res = await userAPI.listResumes();
      setResumes(res.data || []);
    } catch (err) {
      const message =
        err.response?.data?.message ||
        err.response?.data?.error ||
        "Unable to load resumes.";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadResumes();
  }, []);

  const handleFileChange = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setError("");
    setSuccess("");
    setUploading(true);
    setProgress(0);

    try {
      await userAPI.uploadResume(file, (event) => {
        if (event.total) {
          const pct = Math.round((event.loaded * 100) / event.total);
          setProgress(pct);
        }
      });
      setSuccess("Resume uploaded successfully.");
      await loadResumes();
    } catch (err) {
      const message =
        err.response?.data?.message ||
        err.response?.data?.error ||
        "Unable to upload resume.";
      setError(message);
    } finally {
      setUploading(false);
      setProgress(0);
      e.target.value = "";
    }
  };

  const handleDownload = async (resume) => {
    try {
      const res = await userAPI.downloadResume(resume.filename || resume.id);
      const blob = new Blob([res.data], { type: res.data.type });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = resume.originalName || resume.filename || "resume";
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      const message =
        err.response?.data?.message ||
        err.response?.data?.error ||
        "Unable to download resume.";
      setError(message);
    }
  };

  const handleDelete = async (resume) => {
    setError("");
    try {
      await userAPI.deleteResume(resume.filename || resume.id);
      setResumes((prev) =>
        prev.filter(
          (r) =>
            (r.filename || r.id) !== (resume.filename || resume.id)
        )
      );
    } catch (err) {
      const message =
        err.response?.data?.message ||
        err.response?.data?.error ||
        "Unable to delete resume.";
      setError(message);
    }
  };

  if (loading) {
    return <Loader />;
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-2 sm:flex-row sm:items-end">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Resumes</h1>
          <p className="mt-1 text-sm text-slate-500">
            Upload, manage, and download your resumes securely.
          </p>
        </div>
        <div className="flex flex-col items-start gap-2 sm:items-end">
          <label className="inline-flex cursor-pointer items-center justify-center rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-md transition hover:bg-indigo-700">
            <input
              type="file"
              accept=".pdf,.doc,.docx,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
              className="hidden"
              onChange={handleFileChange}
              disabled={uploading}
            />
            {uploading ? "Uploading..." : "Upload resume"}
          </label>
          {uploading && (
            <div className="w-full max-w-xs rounded-full bg-slate-100">
              <div
                className="h-2 rounded-full bg-indigo-600 transition-all"
                style={{ width: `${progress}%` }}
              />
            </div>
          )}
        </div>
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

      <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-md">
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                Name
              </th>
              <th className="hidden px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500 sm:table-cell">
                Uploaded
              </th>
              <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wide text-slate-500">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200 bg-white">
            {Array.isArray(resumes) && resumes.length > 0 ? (
              resumes.map((resume) => (
                <tr key={resume.id || resume.filename}>
                  <td className="px-4 py-3 text-sm text-slate-800">
                    {resume.originalName || resume.filename || "Resume"}
                  </td>
                  <td className="hidden px-4 py-3 text-xs text-slate-500 sm:table-cell">
                    {resume.createdAt
                      ? new Date(resume.createdAt).toLocaleString()
                      : "—"}
                  </td>
                  <td className="px-4 py-3 text-right text-xs">
                    <div className="inline-flex gap-2">
                      <button
                        type="button"
                        onClick={() => handleDownload(resume)}
                        className="rounded-lg border border-slate-200 px-3 py-1.5 font-medium text-slate-700 transition hover:bg-slate-50"
                      >
                        Download
                      </button>
                      <button
                        type="button"
                        onClick={() => handleDelete(resume)}
                        className="rounded-lg border border-red-200 px-3 py-1.5 font-medium text-red-600 transition hover:bg-red-50"
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td
                  colSpan={3}
                  className="px-4 py-6 text-center text-sm text-slate-500"
                >
                  No resumes uploaded yet. Upload your first resume to get
                  started.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default ResumePage;

