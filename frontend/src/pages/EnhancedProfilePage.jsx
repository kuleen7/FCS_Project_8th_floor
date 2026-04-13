import { useEffect, useMemo, useState } from "react";
import { authAPI, socialAPI, userAPI } from "../services/api";

function EnhancedProfilePage() {
  const [profile, setProfile] = useState(null);
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [info, setInfo] = useState("");
  const [formData, setFormData] = useState({
    first_name: "",
    last_name: "",
    mobile: "",
    headline: "",
    location: "",
    bio: "",
    privacy_level: "public",
  });

  const [viewerIdentity, setViewerIdentity] = useState(true);
  const [connections, setConnections] = useState([]);
  const [graph, setGraph] = useState({ nodes: [], edges: [] });
  const [targetUserId, setTargetUserId] = useState("");
  const [targetProfile, setTargetProfile] = useState(null);
  const [totpSetup, setTotpSetup] = useState(null);
  const [totpCode, setTotpCode] = useState("");
  const [totpLoading, setTotpLoading] = useState(false);

  const loadAll = async () => {
    setLoading(true);
    setError("");
    try {
      const [profileRes, connectionsRes, graphRes] = await Promise.all([
        userAPI.getProfile(),
        socialAPI.listConnections(true),
        socialAPI.graph(1),
      ]);
      const p = profileRes.data || {};
      setProfile(p);
      setFormData((prev) => ({
        ...prev,
        first_name: p.first_name || "",
        last_name: p.last_name || "",
        mobile: p.mobile || "",
        headline: p.headline || "",
        location: p.location || "",
        bio: p.bio || "",
        privacy_level: p.privacy_level || "public",
      }));
      setConnections(connectionsRes.data?.connections || []);
      setGraph(graphRes.data || { nodes: [], edges: [] });
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to load profile workspace");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAll();
  }, []);

  const acceptedConnections = useMemo(
    () => connections.filter((c) => String(c.status).toLowerCase() === "accepted"),
    [connections]
  );
  const pendingConnections = useMemo(
    () => connections.filter((c) => String(c.status).toLowerCase() === "pending"),
    [connections]
  );

  const handleSaveProfile = async () => {
    setSaving(true);
    setError("");
    setInfo("");
    try {
      await userAPI.updateProfile(formData);
      setInfo("Profile updated.");
      setEditing(false);
      await loadAll();
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to update profile");
    } finally {
      setSaving(false);
    }
  };

  const handleSendConnectionRequest = async () => {
    if (!targetUserId.trim()) return;
    setError("");
    setInfo("");
    try {
      await socialAPI.sendConnectionRequest(Number(targetUserId));
      setInfo("Connection request sent.");
      await loadAll();
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to send request");
    }
  };

  const handleAcceptConnection = async (connectionId) => {
    try {
      await socialAPI.acceptConnection(connectionId);
      await loadAll();
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to accept connection");
    }
  };

  const handleRemoveConnection = async (connectionId) => {
    try {
      await socialAPI.removeConnection(connectionId);
      await loadAll();
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to remove connection");
    }
  };

  const handleLookupProfile = async () => {
    if (!targetUserId.trim()) return;
    setTargetProfile(null);
    setError("");
    try {
      const res = await userAPI.viewProfile(Number(targetUserId));
      setTargetProfile(res.data || null);
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to view profile");
    }
  };

  const handleUpdateViewerIdentity = async () => {
    setError("");
    try {
      await socialAPI.updateViewerSetting(viewerIdentity);
      setInfo("Viewer identity setting updated.");
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to update viewer setting");
    }
  };

  const handleTotpSetup = async () => {
    setTotpLoading(true);
    setError("");
    try {
      const res = await authAPI.setupTotp2FA();
      setTotpSetup(res.data?.data || null);
      setInfo("TOTP secret generated. Add it in Authenticator and enable with code.");
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to initialize TOTP");
    } finally {
      setTotpLoading(false);
    }
  };

  const handleEnableTotp = async () => {
    if (!totpCode.trim()) return;
    setTotpLoading(true);
    setError("");
    try {
      await authAPI.enableTotp2FA(totpCode.trim());
      setInfo("2FA enabled successfully.");
      setTotpCode("");
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to enable TOTP");
    } finally {
      setTotpLoading(false);
    }
  };

  const handleDisableTotp = async () => {
    if (!totpCode.trim()) return;
    setTotpLoading(true);
    setError("");
    try {
      await authAPI.disableTotp2FA(totpCode.trim());
      setInfo("2FA disabled.");
      setTotpCode("");
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to disable TOTP");
    } finally {
      setTotpLoading(false);
    }
  };

  if (loading) return <div className="p-4">Loading profile workspace...</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold">Profile & Security Center</h2>
        <button className="rounded border px-3 py-1.5 text-sm" onClick={loadAll}>
          Refresh
        </button>
      </div>

      {error ? <p className="rounded border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">{error}</p> : null}
      {info ? <p className="rounded border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-700">{info}</p> : null}

      <div className="rounded-lg border bg-white p-4">
        <div className="mb-3 flex items-center justify-between">
          <h3 className="font-semibold">Profile</h3>
          <button className="rounded border px-3 py-1 text-sm" onClick={() => setEditing((v) => !v)}>
            {editing ? "Cancel" : "Edit"}
          </button>
        </div>
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
          <input className="rounded border px-3 py-2" placeholder="First name" value={formData.first_name} disabled={!editing} onChange={(e) => setFormData({ ...formData, first_name: e.target.value })} />
          <input className="rounded border px-3 py-2" placeholder="Last name" value={formData.last_name} disabled={!editing} onChange={(e) => setFormData({ ...formData, last_name: e.target.value })} />
          <input className="rounded border px-3 py-2" placeholder="Mobile" value={formData.mobile} disabled={!editing} onChange={(e) => setFormData({ ...formData, mobile: e.target.value })} />
          <input className="rounded border px-3 py-2" placeholder="Headline" value={formData.headline} disabled={!editing} onChange={(e) => setFormData({ ...formData, headline: e.target.value })} />
          <input className="rounded border px-3 py-2" placeholder="Location" value={formData.location} disabled={!editing} onChange={(e) => setFormData({ ...formData, location: e.target.value })} />
          <select className="rounded border px-3 py-2" value={formData.privacy_level} disabled={!editing} onChange={(e) => setFormData({ ...formData, privacy_level: e.target.value })}>
            <option value="public">Public</option>
            <option value="connections">Connections-only</option>
            <option value="private">Private</option>
          </select>
          <textarea className="rounded border px-3 py-2 md:col-span-2" rows={3} placeholder="Bio" value={formData.bio} disabled={!editing} onChange={(e) => setFormData({ ...formData, bio: e.target.value })} />
        </div>
        {editing ? (
          <div className="mt-3">
            <button disabled={saving} onClick={handleSaveProfile} className="rounded bg-indigo-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-60">
              {saving ? "Saving..." : "Save Profile"}
            </button>
          </div>
        ) : null}
        <p className="mt-3 text-xs text-slate-500">Viewer count: {targetProfile?.viewer_count ?? profile?.viewer_count ?? "Open your own profile via view lookup to see latest server value."}</p>
      </div>

      <div className="rounded-lg border bg-white p-4">
        <h3 className="mb-3 font-semibold">Authenticator (TOTP) 2FA</h3>
        <div className="flex flex-wrap items-center gap-2">
          <button disabled={totpLoading} onClick={handleTotpSetup} className="rounded border px-3 py-2 text-sm">
            {totpLoading ? "Preparing..." : "Setup 2FA"}
          </button>
          <input
            className="rounded border px-3 py-2 text-sm"
            placeholder="6-digit code"
            value={totpCode}
            onChange={(e) => setTotpCode(e.target.value)}
          />
          <button disabled={totpLoading} onClick={handleEnableTotp} className="rounded border px-3 py-2 text-sm">
            Enable
          </button>
          <button disabled={totpLoading} onClick={handleDisableTotp} className="rounded border px-3 py-2 text-sm">
            Disable
          </button>
        </div>
        {totpSetup ? (
          <div className="mt-3 space-y-2 rounded border border-slate-200 bg-slate-50 p-3 text-sm">
            <p><span className="font-medium">Secret:</span> {totpSetup.totp_secret}</p>
            <p className="break-all"><span className="font-medium">Provisioning URI:</span> {totpSetup.provisioning_uri}</p>
          </div>
        ) : null}
      </div>

      <div className="rounded-lg border bg-white p-4">
        <h3 className="mb-3 font-semibold">Connections</h3>
        <div className="mb-3 flex flex-wrap gap-2">
          <input
            className="rounded border px-3 py-2 text-sm"
            placeholder="Target user ID"
            value={targetUserId}
            onChange={(e) => setTargetUserId(e.target.value)}
          />
          <button onClick={handleSendConnectionRequest} className="rounded border px-3 py-2 text-sm">
            Send Request
          </button>
          <button onClick={handleLookupProfile} className="rounded border px-3 py-2 text-sm">
            View Profile by ID
          </button>
        </div>

        {targetProfile ? (
          <div className="mb-3 rounded border border-slate-200 bg-slate-50 p-3 text-sm">
            <p className="font-medium">Profile #{targetProfile.id}</p>
            <p>{targetProfile.first_name} {targetProfile.last_name}</p>
            <p className="text-slate-600">{targetProfile.headline || "No headline"}</p>
            {typeof targetProfile.viewer_count === "number" ? (
              <p className="text-slate-600">Viewer count: {targetProfile.viewer_count}</p>
            ) : null}
          </div>
        ) : null}

        <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
          <div className="rounded border p-3">
            <p className="mb-2 text-sm font-medium">Pending ({pendingConnections.length})</p>
            <div className="space-y-2">
              {pendingConnections.map((c) => (
                <div key={c.connection_id} className="rounded border p-2 text-sm">
                  <p>{c.name || c.email || `User #${c.user_id}`}</p>
                  <div className="mt-1 flex gap-2">
                    <button onClick={() => handleAcceptConnection(c.connection_id)} className="rounded border px-2 py-1 text-xs">Accept</button>
                    <button onClick={() => handleRemoveConnection(c.connection_id)} className="rounded border px-2 py-1 text-xs text-rose-600">Remove</button>
                  </div>
                </div>
              ))}
              {pendingConnections.length === 0 ? <p className="text-xs text-slate-500">No pending requests.</p> : null}
            </div>
          </div>

          <div className="rounded border p-3">
            <p className="mb-2 text-sm font-medium">Accepted ({acceptedConnections.length})</p>
            <div className="space-y-2">
              {acceptedConnections.map((c) => (
                <div key={c.connection_id} className="rounded border p-2 text-sm">
                  <p>{c.name || c.email || `User #${c.user_id}`}</p>
                  <button onClick={() => handleRemoveConnection(c.connection_id)} className="mt-1 rounded border px-2 py-1 text-xs text-rose-600">
                    Remove
                  </button>
                </div>
              ))}
              {acceptedConnections.length === 0 ? <p className="text-xs text-slate-500">No accepted connections.</p> : null}
            </div>
          </div>
        </div>
      </div>

      <div className="rounded-lg border bg-white p-4">
        <h3 className="mb-3 font-semibold">Viewer Privacy & Graph</h3>
        <div className="mb-3 flex items-center gap-2">
          <input
            id="showIdentity"
            type="checkbox"
            checked={viewerIdentity}
            onChange={(e) => setViewerIdentity(e.target.checked)}
          />
          <label htmlFor="showIdentity" className="text-sm">Show my identity in others&apos; recent viewers</label>
          <button onClick={handleUpdateViewerIdentity} className="rounded border px-3 py-1 text-sm">Save</button>
        </div>
        <p className="text-sm text-slate-600">
          Connection graph nodes: {graph.nodes?.length || 0}, edges: {graph.edges?.length || 0}
        </p>
      </div>
    </div>
  );
}

export default EnhancedProfilePage;
