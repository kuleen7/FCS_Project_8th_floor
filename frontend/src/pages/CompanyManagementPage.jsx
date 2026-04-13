import { useEffect, useState } from "react";
import { companyAPI } from "../services/api";

function CompanyManagementPage() {
  const [companies, setCompanies] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [formData, setFormData] = useState({ name: "", description: "", location: "", website: "" });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const res = await companyAPI.listMyCompanies();
        const list = res.data || [];
        setCompanies(list);
        if (list.length) {
          setSelectedId(list[0].id);
          setFormData({
            name: list[0].name || "",
            description: list[0].description || "",
            location: list[0].location || "",
            website: list[0].website || "",
          });
        }
      } catch (err) {
        setError(err.response?.data?.detail || "Failed to load companies");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await companyAPI.createCompany(formData);
      const res = await companyAPI.listMyCompanies();
      setCompanies(res.data || []);
      setFormData({ name: "", description: "", location: "", website: "" });
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to create company");
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
          <p className="mt-4 text-slate-600">Loading company data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Company Management</h1>
      {error ? <p className="text-sm text-red-600">{error}</p> : null}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <div className="rounded border bg-white p-4">
          <h2 className="mb-3 font-medium">Create Company</h2>
          <form onSubmit={handleSubmit} className="space-y-2">
            <input name="name" value={formData.name} onChange={handleInputChange} placeholder="Company name" className="w-full rounded border px-3 py-2" required />
            <input name="location" value={formData.location} onChange={handleInputChange} placeholder="Location" className="w-full rounded border px-3 py-2" />
            <input name="website" value={formData.website} onChange={handleInputChange} placeholder="Website" className="w-full rounded border px-3 py-2" />
            <textarea name="description" value={formData.description} onChange={handleInputChange} placeholder="Description" className="w-full rounded border px-3 py-2" />
            <button type="submit" className="rounded bg-indigo-600 px-4 py-2 text-white">Create</button>
          </form>
        </div>
        <div className="rounded border bg-white p-4">
          <h2 className="mb-3 font-medium">My Companies</h2>
          <div className="space-y-2">
            {companies.map((c) => (
              <div key={c.id} className={`rounded border p-3 ${selectedId === c.id ? "border-indigo-500 bg-indigo-50" : ""}`}>
                <p className="font-medium">#{c.id} {c.name}</p>
                <p className="text-sm text-slate-600">{c.location || "No location"}</p>
                <p className="text-xs text-slate-500">{c.description || "No description"}</p>
              </div>
            ))}
            {companies.length === 0 ? <p className="text-sm text-slate-500">No companies yet.</p> : null}
          </div>
        </div>
      </div>
    </div>
  );
}

export default CompanyManagementPage;
