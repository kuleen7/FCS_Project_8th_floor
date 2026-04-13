import { useCallback, useEffect, useState } from "react";
import { buildOtpOnlyHeaders, jobsAPI, userAPI } from "../services/api";

function EnhancedResumePage() {
  const [resumes, setResumes] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [selectedJobId, setSelectedJobId] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);
  const [matchResult, setMatchResult] = useState(null);
  const [parseResult, setParseResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [role, setRole] = useState("user");

  const loadData = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [resumeRes, jobsSearchRes] = await Promise.all([
        userAPI.listResumes(),
        jobsAPI.search({ page: 1, limit: 50 }),
      ]);
      const list = resumeRes.data?.resumes || [];
      setResumes(list);
      let jobsList = jobsSearchRes.data?.jobs || [];
      if (!jobsList.length) {
        const myJobs = await jobsAPI.myPostings();
        jobsList = myJobs.data || [];
      }
      setJobs(jobsList);
      if (jobsList.length && !selectedJobId) {
        setSelectedJobId(String(jobsList[0].id));
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load resumes");
    } finally {
      setLoading(false);
    }
  }, [selectedJobId]);

  useEffect(() => {
    try {
      const user = JSON.parse(localStorage.getItem("user") || "{}");
      setRole(user.role || "user");
    } catch {
      setRole("user");
    }
    loadData();
  }, [loadData]);

  if (role === "admin") {
    return (
      <div className="rounded border border-amber-300 bg-amber-50 p-4 text-amber-800">
        Resume tools are available for job-seekers/recruiters only.
      </div>
    );
  }

  const onUpload = async () => {
    if (!selectedFile) return;
    try {
      await userAPI.uploadResume(selectedFile);
      setSelectedFile(null);
      await loadData();
    } catch (err) {
      setError(err.response?.data?.detail || "Upload failed");
    }
  };

  const onDownload = async (filename) => {
    try {
      const headers = await buildOtpOnlyHeaders();
      const res = await userAPI.downloadResume(filename, headers);
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const a = document.createElement("a");
      a.href = url;
      a.download = filename.replace(".encrypted", "");
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "Download failed");
    }
  };

  const onDelete = async (filename) => {
    if (!window.confirm("Delete this resume?")) return;
    try {
      const headers = await buildOtpOnlyHeaders();
      await userAPI.deleteResume(filename, headers);
      await loadData();
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "Delete failed");
    }
  };

  const onParse = async (filename) => {
    try {
      const res = await userAPI.parseResume(filename);
      setParseResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Parse failed");
    }
  };

  const onMatch = async (filename) => {
    if (!selectedJobId) {
      setError("Create/select a job first to run matching");
      return;
    }
    try {
      const res = await userAPI.matchResume(filename, selectedJobId);
      setMatchResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Match failed");
    }
  };

  if (loading) return <div className="p-4">Loading resume workspace...</div>;

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-semibold">Resume Management (April Bonus)</h2>
      {error ? <p className="text-sm text-red-600">{error}</p> : null}
      <p className="text-sm text-slate-600">
        Download/delete require virtual keyboard OTP. Parse/match use April intelligent resume APIs.
      </p>

      <div className="rounded border p-4">
        <input type="file" onChange={(e) => setSelectedFile(e.target.files?.[0] || null)} />
        <button className="ml-2 rounded bg-indigo-600 px-3 py-1 text-white" onClick={onUpload}>
          Upload
        </button>
      </div>

      <div className="rounded border p-4">
        <label className="mb-1 block text-sm">Job for matching</label>
        <select
          className="w-full rounded border px-3 py-2"
          value={selectedJobId}
          onChange={(e) => setSelectedJobId(e.target.value)}
        >
          <option value="">Select job</option>
          {jobs.map((job) => (
            <option key={job.id} value={job.id}>
              #{job.id} - {job.title}
            </option>
          ))}
        </select>
      </div>

      <div className="space-y-2">
        {resumes.map((filename) => (
          <div key={filename} className="rounded border p-3">
            <p className="text-sm">{filename}</p>
            <div className="mt-2 flex flex-wrap gap-2">
              <button className="rounded border px-3 py-1" onClick={() => onDownload(filename)}>
                Download (OTP)
              </button>
              <button className="rounded border px-3 py-1 text-red-600" onClick={() => onDelete(filename)}>
                Delete (OTP)
              </button>
              <button className="rounded border px-3 py-1" onClick={() => onParse(filename)}>
                Parse Resume
              </button>
              <button className="rounded border px-3 py-1" onClick={() => onMatch(filename)}>
                Match to Job
              </button>
            </div>
          </div>
        ))}
        {resumes.length === 0 ? <p className="text-sm text-slate-500">No resumes uploaded.</p> : null}
      </div>

      {parseResult ? (
        <div className="rounded border p-4">
          <h3 className="mb-2 font-semibold">Parse Result</h3>
          <pre className="overflow-auto text-xs">{JSON.stringify(parseResult, null, 2)}</pre>
        </div>
      ) : null}

      {matchResult ? (
        <div className="rounded border p-4">
          <h3 className="mb-2 font-semibold">Match Result</h3>
          <pre className="overflow-auto text-xs">{JSON.stringify(matchResult, null, 2)}</pre>
        </div>
      ) : null}
    </div>
  );
}

export default EnhancedResumePage;
