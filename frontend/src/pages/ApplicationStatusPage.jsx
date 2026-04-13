import { useEffect, useMemo, useState } from "react";
import { applicationsAPI, companyAPI, jobsAPI } from "../services/api";

function ApplicationStatusPage() {
  const [applications, setApplications] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [selectedJobId, setSelectedJobId] = useState("");
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");
  const [error, setError] = useState("");
  const [refreshing, setRefreshing] = useState(false);
  const userData = JSON.parse(localStorage.getItem("user") || "{}");
  const isRecruiter = userData.role === "recruiter";

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError("");
      try {
        if (isRecruiter) {
          const [companiesRes, myPostingsRes] = await Promise.all([
            companyAPI.listMyCompanies(),
            jobsAPI.myPostings(),
          ]);
          const companies = companiesRes.data || [];
          const myPostings = myPostingsRes.data || [];

          let companyJobs = [];
          if (companies.length) {
            const jobResults = await Promise.all(
              companies.map((company) => jobsAPI.companyJobs(company.id, false))
            );
            companyJobs = jobResults.flatMap((res) => res.data || []);
          }

          // Merge both sources so older data/membership inconsistencies do not hide recruiter jobs.
          const dedupedJobs = Array.from(
            new Map([...myPostings, ...companyJobs].map((job) => [job.id, job])).values()
          );
          setJobs(dedupedJobs);
          if (dedupedJobs.length) {
            const initialJobId = selectedJobId || String(dedupedJobs[0].id);
            setSelectedJobId(initialJobId);
            const appsRes = await applicationsAPI.recruiterApplicants(initialJobId);
            setApplications(appsRes.data || []);
          } else {
            setApplications([]);
            setError("No recruiter jobs found yet. Create a job first, then refresh applicants.");
          }
        } else {
          const res = await applicationsAPI.myApplications();
          setApplications(res.data || []);
        }
      } catch (err) {
        setError(err.response?.data?.detail || "Failed to load applications");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [isRecruiter, selectedJobId]);

  const refreshApplicants = async () => {
    if (!selectedJobId) return;
    setRefreshing(true);
    setError("");
    try {
      const appsRes = await applicationsAPI.recruiterApplicants(selectedJobId);
      setApplications(appsRes.data || []);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to refresh applicants");
    } finally {
      setRefreshing(false);
    }
  };

  const filteredApplications = useMemo(() => {
    if (filter === "all") return applications;
    return applications.filter((app) => String(app.status || "").toLowerCase() === filter);
  }, [applications, filter]);

  const getStatusColor = (status) => {
    switch (status) {
      case "applied": return "bg-blue-100 text-blue-800";
      case "reviewed": return "bg-yellow-100 text-yellow-800";
      case "interviewed": return "bg-purple-100 text-purple-800";
      case "rejected": return "bg-red-100 text-red-800";
      case "offer": return "bg-green-100 text-green-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  const updateApplicantStatus = async (applicationId, newStatus) => {
    try {
      await applicationsAPI.update(applicationId, { status: newStatus });
      const appsRes = await applicationsAPI.recruiterApplicants(selectedJobId);
      setApplications(appsRes.data || []);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to update status");
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
          <p className="mt-4 text-slate-600">Loading applications...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h1 className="text-2xl font-semibold">{isRecruiter ? "Applicant Management" : "My Applications"}</h1>
        <div className="flex gap-2">
          {isRecruiter ? (
            <>
              <select
                value={selectedJobId}
                onChange={async (e) => {
                  const id = e.target.value;
                  setSelectedJobId(id);
                  if (!id) {
                    setApplications([]);
                    return;
                  }
                  const appsRes = await applicationsAPI.recruiterApplicants(id);
                  setApplications(appsRes.data || []);
                }}
                className="rounded border px-3 py-2 text-sm"
              >
                <option value="">Select job</option>
                {jobs.map((job) => (
                  <option key={job.id} value={job.id}>
                    #{job.id} {job.title}
                  </option>
                ))}
              </select>
              <button
                type="button"
                onClick={refreshApplicants}
                disabled={!selectedJobId || refreshing}
                className="rounded border px-3 py-2 text-sm"
              >
                {refreshing ? "Refreshing..." : "Refresh Applicants"}
              </button>
            </>
          ) : null}
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="rounded border px-3 py-2 text-sm"
          >
            <option value="all">All Status</option>
            <option value="applied">Applied</option>
            <option value="reviewed">Reviewed</option>
            <option value="interviewed">Interviewed</option>
            <option value="rejected">Rejected</option>
            <option value="offer">Offer</option>
          </select>
        </div>
      </div>
      {error ? <p className="text-sm text-red-600">{error}</p> : null}
      <main>
        {!isRecruiter ? (
          <div className="space-y-6">
            {filteredApplications.map((app) => (
              <div key={app.id} className="bg-white shadow rounded-lg p-6">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h3 className="text-lg font-medium text-slate-900">{app.job?.title || `Job #${app.job_id}`}</h3>
                    <p className="text-sm text-slate-500">Applied: {new Date(app.applied_at).toLocaleDateString()}</p>
                    <div className="mt-4 flex items-center space-x-4 text-sm text-slate-500">
                      <span>Status: {app.status}</span>
                    </div>
                  </div>
                  <div className="ml-4">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(String(app.status).toLowerCase())}`}>
                      {app.status}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="space-y-6">
            {filteredApplications.map((app) => (
              <div key={app.id} className="rounded-lg border bg-white p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">
                      {app.applicant
                        ? `${app.applicant.first_name || ""} ${app.applicant.last_name || ""}`.trim() || app.applicant.email
                        : `Applicant #${app.applicant_id}`}
                    </p>
                    {app.applicant?.email ? (
                      <p className="text-sm text-slate-600">{app.applicant.email}</p>
                    ) : null}
                    <p className="text-sm text-slate-500">Applied: {new Date(app.applied_at).toLocaleString()}</p>
                  </div>
                  <select
                    value={String(app.status)}
                    onChange={(e) => updateApplicantStatus(app.id, e.target.value)}
                    className="rounded border px-2 py-1 text-sm"
                  >
                    <option value="Applied">Applied</option>
                    <option value="Reviewed">Reviewed</option>
                    <option value="Interviewed">Interviewed</option>
                    <option value="Rejected">Rejected</option>
                    <option value="Offer">Offer</option>
                  </select>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

export default ApplicationStatusPage;
