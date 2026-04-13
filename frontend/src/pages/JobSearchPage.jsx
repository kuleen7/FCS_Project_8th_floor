import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { applicationsAPI, jobsAPI } from "../services/api";

function formatType(jobType) {
  const raw = String(jobType || "").replace(/_/g, " ").trim();
  return raw ? raw.charAt(0).toUpperCase() + raw.slice(1) : "N/A";
}

function formatSalary(job) {
  const hasMin = typeof job.salary_min === "number";
  const hasMax = typeof job.salary_max === "number";
  if (!hasMin && !hasMax) return "Not specified";
  if (hasMin && hasMax) return `$${job.salary_min.toLocaleString()} - $${job.salary_max.toLocaleString()}`;
  if (hasMin) return `$${job.salary_min.toLocaleString()}+`;
  return `Up to $${job.salary_max.toLocaleString()}`;
}

function JobSearchPage() {
  const navigate = useNavigate();
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedLocation, setSelectedLocation] = useState("");
  const [selectedType, setSelectedType] = useState("");
  const [selectedSalary, setSelectedSalary] = useState("");
  const [myAppliedJobIds, setMyAppliedJobIds] = useState(new Set());
  const [applyingJobId, setApplyingJobId] = useState(null);

  const loadData = async () => {
    setLoading(true);
    setError("");
    try {
      const [searchRes, myAppsRes] = await Promise.all([
        jobsAPI.search({ page: 1, limit: 100 }),
        applicationsAPI.myApplications(),
      ]);
      const jobsList = searchRes.data?.jobs || [];
      setJobs(jobsList);
      const appliedIds = new Set((myAppsRes.data || []).map((app) => app.job_id));
      setMyAppliedJobIds(appliedIds);
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to load jobs");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const userData = localStorage.getItem("user");
    if (!userData) {
      navigate("/login");
      return;
    }
    loadData();
  }, [navigate]);

  const locations = useMemo(
    () => Array.from(new Set(jobs.map((j) => j.location).filter(Boolean))).sort(),
    [jobs]
  );
  const jobTypes = useMemo(
    () => Array.from(new Set(jobs.map((j) => j.job_type).filter(Boolean))).sort(),
    [jobs]
  );

  const filteredJobs = useMemo(() => {
    let filtered = jobs;
    if (searchTerm.trim()) {
      const needle = searchTerm.trim().toLowerCase();
      filtered = filtered.filter((job) =>
        [job.title, job.company?.name, job.description, job.required_skills]
          .filter(Boolean)
          .join(" ")
          .toLowerCase()
          .includes(needle)
      );
    }
    if (selectedLocation) {
      filtered = filtered.filter((job) => job.location === selectedLocation);
    }
    if (selectedType) {
      filtered = filtered.filter((job) => job.job_type === selectedType);
    }
    if (selectedSalary) {
      filtered = filtered.filter((job) => (job.salary_min || 0) >= Number(selectedSalary));
    }
    return filtered;
  }, [jobs, searchTerm, selectedLocation, selectedType, selectedSalary]);

  const handleApply = async (jobId) => {
    if (myAppliedJobIds.has(jobId)) return;
    setApplyingJobId(jobId);
    setError("");
    try {
      await applicationsAPI.apply({ job_id: jobId, cover_note: "Applied from job search page." });
      const updated = new Set(myAppliedJobIds);
      updated.add(jobId);
      setMyAppliedJobIds(updated);
      alert("Application submitted successfully.");
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to apply for this job");
    } finally {
      setApplyingJobId(null);
    }
  };

  if (loading) {
    return <div className="p-6 text-sm text-slate-600">Loading job opportunities...</div>;
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <h1 className="text-xl font-semibold text-slate-900">Job Search</h1>
          <button onClick={() => navigate("/dashboard")} className="text-slate-600 hover:text-slate-900">
            Back to Dashboard
          </button>
        </div>
      </div>

      <main className="mx-auto max-w-7xl space-y-4 px-4 py-6 sm:px-6 lg:px-8">
        {error ? <p className="rounded border border-rose-200 bg-rose-50 p-3 text-sm text-rose-700">{error}</p> : null}

        <div className="rounded-lg bg-white p-6 shadow">
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-5">
            <div className="lg:col-span-2">
              <label className="mb-2 block text-sm font-medium text-slate-700">Search Jobs</label>
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search by title, company, or skills..."
                className="w-full rounded-lg border border-slate-300 px-3 py-2"
              />
            </div>
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">Location</label>
              <select value={selectedLocation} onChange={(e) => setSelectedLocation(e.target.value)} className="w-full rounded-lg border border-slate-300 px-3 py-2">
                <option value="">All Locations</option>
                {locations.map((location) => (
                  <option key={location} value={location}>
                    {location}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">Job Type</label>
              <select value={selectedType} onChange={(e) => setSelectedType(e.target.value)} className="w-full rounded-lg border border-slate-300 px-3 py-2">
                <option value="">All Types</option>
                {jobTypes.map((jobType) => (
                  <option key={jobType} value={jobType}>
                    {formatType(jobType)}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">Min Salary</label>
              <select value={selectedSalary} onChange={(e) => setSelectedSalary(e.target.value)} className="w-full rounded-lg border border-slate-300 px-3 py-2">
                <option value="">Any</option>
                <option value="30000">$30,000+</option>
                <option value="50000">$50,000+</option>
                <option value="80000">$80,000+</option>
                <option value="100000">$100,000+</option>
              </select>
            </div>
          </div>
          <div className="mt-4 flex items-center justify-between">
            <p className="text-sm text-slate-600">{filteredJobs.length} jobs found</p>
            <button
              onClick={() => {
                setSearchTerm("");
                setSelectedLocation("");
                setSelectedType("");
                setSelectedSalary("");
              }}
              className="text-sm text-indigo-600 hover:text-indigo-800"
            >
              Clear Filters
            </button>
          </div>
        </div>

        <div className="space-y-4">
          {filteredJobs.length === 0 ? (
            <div className="rounded-lg bg-white p-8 text-center shadow">
              <p className="text-slate-600">No jobs found. Try clearing filters.</p>
            </div>
          ) : (
            filteredJobs.map((job) => {
              const applied = myAppliedJobIds.has(job.id);
              return (
                <div key={job.id} className="rounded-lg bg-white p-6 shadow">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-slate-900">{job.title}</h3>
                      <p className="mt-1 text-slate-600">{job.company?.name || `Company #${job.company_id}`}</p>
                      <p className="mt-3 text-sm text-slate-700">{job.description}</p>
                      <div className="mt-4 grid grid-cols-1 gap-2 text-sm text-slate-600 md:grid-cols-3">
                        <div>Location: {job.location || "N/A"}</div>
                        <div>Type: {formatType(job.job_type)}</div>
                        <div>Salary: {formatSalary(job)}</div>
                      </div>
                    </div>
                    <button
                      onClick={() => handleApply(job.id)}
                      disabled={applied || applyingJobId === job.id}
                      className={`rounded-lg px-4 py-2 text-sm font-medium ${
                        applied
                          ? "cursor-not-allowed bg-slate-100 text-slate-400"
                          : "bg-indigo-600 text-white hover:bg-indigo-700"
                      }`}
                    >
                      {applied ? "Applied" : applyingJobId === job.id ? "Applying..." : "Apply Now"}
                    </button>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </main>
    </div>
  );
}

export default JobSearchPage;
