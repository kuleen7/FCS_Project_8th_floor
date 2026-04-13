import { useEffect, useMemo, useState } from "react";
import { buildHighRiskHeaders, companyAPI, jobsAPI } from "../services/api";

const initialForm = {
  title: "",
  description: "",
  required_skills: "",
  location: "",
  job_type: "full_time",
};

function JobManagementPage() {
  const [jobs, setJobs] = useState([]);
  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [creatingCompany, setCreatingCompany] = useState(false);
  const [newCompanyName, setNewCompanyName] = useState("");
  const [editingJobId, setEditingJobId] = useState(null);
  const [form, setForm] = useState(initialForm);
  const [error, setError] = useState("");

  const [selectedCompanyId, setSelectedCompanyId] = useState(null);

  const loadData = async () => {
    setLoading(true);
    setError("");
    try {
      const [jobsRes, companiesRes] = await Promise.all([
        jobsAPI.myPostings(),
        companyAPI.listMyCompanies(),
      ]);
      setJobs(jobsRes.data || []);
      const companyList = companiesRes.data || [];
      setCompanies(companyList);
      if (!selectedCompanyId && companyList.length) {
        setSelectedCompanyId(companyList[0].id);
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load jobs");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const resetForm = () => {
    setForm(initialForm);
    setEditingJobId(null);
  };

  const createCompany = async () => {
    if (!newCompanyName.trim()) return;
    setCreatingCompany(true);
    setError("");
    try {
      const res = await companyAPI.createCompany({
        name: newCompanyName.trim(),
        description: "Created from recruiter dashboard",
        location: "Remote",
      });
      const company = res.data;
      setCompanies((prev) => [...prev, company]);
      setSelectedCompanyId(company.id);
      setNewCompanyName("");
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to create company");
    } finally {
      setCreatingCompany(false);
    }
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    if (!selectedCompanyId) {
      setError("Create a company first before posting jobs.");
      return;
    }
    setSubmitting(true);
    setError("");
    try {
      const action = editingJobId ? "job.update" : "job.create";
      const headers = await buildHighRiskHeaders(action);
      const payload = {
        ...form,
        company_id: selectedCompanyId,
      };

      if (editingJobId) {
        await jobsAPI.updateJob(editingJobId, payload, headers);
      } else {
        await jobsAPI.createJob(payload, headers);
      }
      await loadData();
      resetForm();
      window.alert("Job action completed with PKI + virtual OTP verification.");
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "Job request failed");
    } finally {
      setSubmitting(false);
    }
  };

  const onEdit = (job) => {
    setEditingJobId(job.id);
    setForm({
      title: job.title || "",
      description: job.description || "",
      required_skills: job.required_skills || "",
      location: job.location || "",
      job_type: job.job_type || "full_time",
    });
  };

  const onDelete = async (jobId) => {
    if (!window.confirm("Delete this job posting?")) return;
    try {
      await jobsAPI.deleteJob(jobId);
      await loadData();
    } catch (err) {
      setError(err.response?.data?.detail || "Delete failed");
    }
  };

  if (loading) return <div className="p-4">Loading job management...</div>;

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold">Job Management (April Secured)</h2>
      {error ? <p className="text-sm text-red-600">{error}</p> : null}
      <p className="text-sm text-slate-600">
        Protected actions trigger virtual keyboard OTP and PKI signing automatically.
      </p>

      <div className="rounded border p-4">
        <p className="mb-2 text-sm font-medium">Select company for this job</p>
        <select
          className="w-full rounded border px-3 py-2"
          value={selectedCompanyId || ""}
          onChange={(e) => setSelectedCompanyId(Number(e.target.value))}
        >
          <option value="">Select company</option>
          {companies.map((c) => (
            <option key={c.id} value={c.id}>
              #{c.id} - {c.name}
            </option>
          ))}
        </select>
        <div className="mt-3 flex gap-2">
          <input
            className="flex-1 rounded border px-3 py-2"
            placeholder="Create new company name"
            value={newCompanyName}
            onChange={(e) => setNewCompanyName(e.target.value)}
          />
          <button
            type="button"
            disabled={creatingCompany}
            className="rounded border px-3 py-2"
            onClick={createCompany}
          >
            {creatingCompany ? "Creating..." : "Create Company"}
          </button>
        </div>
      </div>

      <form onSubmit={onSubmit} className="space-y-3 rounded border p-4">
        <input
          className="w-full rounded border px-3 py-2"
          placeholder="Title"
          value={form.title}
          onChange={(e) => setForm({ ...form, title: e.target.value })}
          required
        />
        <textarea
          className="w-full rounded border px-3 py-2"
          placeholder="Description"
          value={form.description}
          onChange={(e) => setForm({ ...form, description: e.target.value })}
          required
        />
        <input
          className="w-full rounded border px-3 py-2"
          placeholder="Required skills (comma separated)"
          value={form.required_skills}
          onChange={(e) => setForm({ ...form, required_skills: e.target.value })}
        />
        <input
          className="w-full rounded border px-3 py-2"
          placeholder="Location"
          value={form.location}
          onChange={(e) => setForm({ ...form, location: e.target.value })}
          required
        />
        <select
          className="w-full rounded border px-3 py-2"
          value={form.job_type}
          onChange={(e) => setForm({ ...form, job_type: e.target.value })}
        >
          <option value="full_time">full_time</option>
          <option value="part_time">part_time</option>
          <option value="remote">remote</option>
          <option value="on_site">on_site</option>
          <option value="hybrid">hybrid</option>
          <option value="internship">internship</option>
        </select>
        <div className="flex gap-2">
          <button
            disabled={submitting}
            className="rounded bg-indigo-600 px-4 py-2 text-white disabled:opacity-50"
            type="submit"
          >
            {editingJobId ? "Update Job (Secure)" : "Create Job (Secure)"}
          </button>
          {editingJobId ? (
            <button className="rounded border px-4 py-2" type="button" onClick={resetForm}>
              Cancel Edit
            </button>
          ) : null}
        </div>
      </form>

      <div className="space-y-3">
        {jobs.map((job) => (
          <div key={job.id} className="rounded border p-4">
            <p className="font-semibold">{job.title}</p>
            <p className="text-sm text-slate-600">{job.description}</p>
            <div className="mt-2 flex gap-2">
              <button className="rounded border px-3 py-1" onClick={() => onEdit(job)}>
                Edit (Secure)
              </button>
              <button className="rounded border px-3 py-1 text-red-600" onClick={() => onDelete(job.id)}>
                Delete
              </button>
            </div>
          </div>
        ))}
        {jobs.length === 0 ? <p className="text-sm text-slate-500">No jobs yet.</p> : null}
      </div>
    </div>
  );
}

export default JobManagementPage;
