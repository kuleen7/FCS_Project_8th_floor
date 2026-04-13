import axios from "axios";

const api = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL || "http://localhost:8000/api",
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  register: (userData) => api.post("/auth/register", userData),
  login: (credentials) => api.post("/auth/login", credentials),
  logout: () => api.post("/auth/logout"),
  getCurrentUser: () => api.get("/auth/me"),
  verifyEmail: (data) => api.post("/auth/verify-email", data),
  resendOTP: (data) => api.post("/auth/resend-otp", data),
  requestPasswordResetOtp: (email) =>
    api.post("/auth/resend-otp", { email, otp_type: "password_reset" }),
  resetPasswordWithOtp: (payload) => api.post("/auth/reset-password", payload),
  setupTotp2FA: () => api.post("/auth/2fa/setup"),
  enableTotp2FA: (totp_code) => api.post("/auth/2fa/enable", { totp_code }),
  disableTotp2FA: (totp_code) => api.post("/auth/2fa/disable", { totp_code }),
};

export const userAPI = {
  listUsers: (q = "", limit = 20) => api.get("/users/", { params: { q, limit } }),
  getProfile: () => api.get("/profile/me"),
  updateProfile: (data) => api.put("/profile/me", data),
  uploadProfilePicture: (file) => {
    const formData = new FormData();
    formData.append("file", file);
    return api.post("/profile/upload-picture", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
  },
  uploadResume: (file, onUploadProgress) => {
    const formData = new FormData();
    formData.append("file", file);
    return api.post("/users/resume/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
      onUploadProgress,
    });
  },
  listResumes: () => api.get("/users/resume/list"),
  downloadResume: (filename, headers = {}) =>
    api.get(`/users/resume/download/${encodeURIComponent(filename)}`, {
      responseType: "blob",
      headers,
    }),
  deleteResume: (filename, headers = {}) =>
    api.delete(`/users/resume/${encodeURIComponent(filename)}`, { headers }),
  parseResume: (filename) => api.get(`/users/resume/parse/${encodeURIComponent(filename)}`),
  matchResume: (filename, jobId) =>
    api.get(`/users/resume/match/${encodeURIComponent(filename)}/${jobId}`),
  viewProfile: (userId) => api.get(`/profile/view/${userId}`),
};

export const companyAPI = {
  listMyCompanies: () => api.get("/companies/"),
  createCompany: (payload) => api.post("/companies/", payload),
};

export const jobsAPI = {
  search: (params = {}) => api.get("/jobs/search", { params }),
  myPostings: () => api.get("/jobs/my-postings"),
  companyJobs: (companyId, activeOnly = false) =>
    api.get(`/jobs/company/${companyId}`, { params: { active_only: activeOnly } }),
  statistics: (companyId = null) =>
    api.get("/jobs/statistics/overview", { params: companyId ? { company_id: companyId } : {} }),
  createJob: (payload, headers = {}) => api.post("/jobs/", payload, { headers }),
  updateJob: (jobId, payload, headers = {}) => api.put(`/jobs/${jobId}`, payload, { headers }),
  deleteJob: (jobId) => api.delete(`/jobs/${jobId}`),
};

export const applicationsAPI = {
  apply: (payload) => api.post("/applications/", payload),
  myApplications: () => api.get("/applications/my-applications"),
  recruiterApplicants: (jobId = "") =>
    api.get("/applications/recruiter/my-applicants", { params: jobId ? { job_id: jobId } : {} }),
  jobApplications: (jobId) => api.get(`/applications/job/${jobId}`),
  statistics: (params = {}) => api.get("/applications/statistics/overview", { params }),
  update: (id, payload) => api.put(`/applications/${id}`, payload),
};

export const adminAPI = {
  getUsers: () => api.get("/admin/users"),
  getStats: () => api.get("/admin/stats"),
  suspendUser: (userId, headers = {}) => api.post(`/admin/users/${userId}/suspend`, null, { headers }),
  reactivateUser: (userId, headers = {}) =>
    api.post(`/admin/users/${userId}/reactivate`, null, { headers }),
  deleteUser: (userId, headers = {}) => api.delete(`/admin/users/${userId}`, { headers }),
};

export const auditAPI = {
  systemSummary: (days = 7) => api.get("/audit/summary/system", { params: { days } }),
};

export const aprilAPI = {
  rotateKeys: () => api.post("/april/pki/keys/rotate"),
  signPayload: (data) => api.post("/april/pki/sign", { data }),
  requestHighRiskOtp: () => api.post("/april/otp/high-risk/request"),
  verifyChain: () => api.get("/april/audit/chain/verify"),
  appendBlock: (eventType, payload) => api.post("/april/audit/block", { event_type: eventType, payload }),
};

export const messagesAPI = {
  listUsers: (q = "", limit = 30) => api.get("/messages/user-directory", { params: { q, limit } }),
  resolveParticipants: (emails) => api.post("/messages/resolve-participants", { emails }),
  listConversations: () => api.get("/messages/conversations"),
  createConversation: (payload) => api.post("/messages/conversations", payload),
  getConversationMessages: (conversationId) =>
    api.get(`/messages/conversations/${conversationId}/messages`),
  sendMessage: (conversationId, payload) =>
    api.post(`/messages/conversations/${conversationId}/messages`, payload),
  unreadCount: () => api.get("/messages/unread/count"),
};

export const socialAPI = {
  sendConnectionRequest: (targetUserId) => api.post(`/social/connections/request/${targetUserId}`),
  acceptConnection: (connectionId) => api.post(`/social/connections/${connectionId}/accept`),
  removeConnection: (connectionId) => api.delete(`/social/connections/${connectionId}`),
  listConnections: (includePending = true) =>
    api.get("/social/connections", { params: { include_pending: includePending } }),
  graph: (depth = 1) => api.get("/social/graph", { params: { depth } }),
  updateViewerSetting: (showIdentity) =>
    api.post("/social/viewer-settings", { show_identity: showIdentity }),
};

export const getOtpPositionsFromLayout = (layout, otpCode) => {
  const digits = String(otpCode || "").trim().split("");
  if (digits.length !== 6) {
    throw new Error("OTP must be exactly 6 digits");
  }
  const positions = digits.map((digit) => {
    const idx = layout.indexOf(digit);
    if (idx === -1) {
      throw new Error("Invalid OTP for current virtual keyboard layout");
    }
    return idx;
  });
  return positions.join(",");
};

const collectVirtualOtpPositions = (challenge, actionLabel = "Secure action") =>
  new Promise((resolve, reject) => {
    const layout = challenge.layout || [];
    const selectedPositions = [];

    const cleanup = () => {
      if (overlay && overlay.parentNode) {
        overlay.parentNode.removeChild(overlay);
      }
    };

    const submit = () => {
      if (selectedPositions.length !== 6) {
        errorText.textContent = "Select 6 digits using the virtual keyboard.";
        return;
      }
      cleanup();
      resolve(selectedPositions.join(","));
    };

    const cancel = () => {
      cleanup();
      reject(new Error("OTP is required to continue"));
    };

    const overlay = document.createElement("div");
    overlay.style.position = "fixed";
    overlay.style.inset = "0";
    overlay.style.background = "rgba(15,23,42,0.45)";
    overlay.style.zIndex = "99999";
    overlay.style.display = "flex";
    overlay.style.alignItems = "center";
    overlay.style.justifyContent = "center";

    const modal = document.createElement("div");
    modal.style.width = "min(92vw, 420px)";
    modal.style.background = "#fff";
    modal.style.borderRadius = "12px";
    modal.style.padding = "16px";
    modal.style.boxShadow = "0 18px 50px rgba(2,6,23,0.25)";
    modal.style.fontFamily = "system-ui, -apple-system, Segoe UI, Roboto, sans-serif";

    const title = document.createElement("h3");
    title.textContent = "Virtual Keyboard OTP";
    title.style.margin = "0 0 8px 0";
    title.style.fontSize = "18px";

    const subtitle = document.createElement("p");
    subtitle.textContent = `${actionLabel}: tap OTP digits in order on this randomized keypad.`;
    subtitle.style.margin = "0 0 10px 0";
    subtitle.style.fontSize = "13px";
    subtitle.style.color = "#475569";

    const selectedBox = document.createElement("div");
    selectedBox.style.marginBottom = "10px";
    selectedBox.style.padding = "8px";
    selectedBox.style.border = "1px solid #cbd5e1";
    selectedBox.style.borderRadius = "8px";
    selectedBox.style.fontSize = "16px";
    selectedBox.style.letterSpacing = "4px";
    selectedBox.textContent = "_ _ _ _ _ _";

    const keypad = document.createElement("div");
    keypad.style.display = "grid";
    keypad.style.gridTemplateColumns = "repeat(5, minmax(0, 1fr))";
    keypad.style.gap = "8px";
    keypad.style.marginBottom = "10px";

    const renderSelected = () => {
      const chars = selectedPositions.map((idx) => layout[idx] ?? "?");
      const placeholders = new Array(6 - chars.length).fill("_");
      selectedBox.textContent = [...chars, ...placeholders].join(" ");
    };

    layout.forEach((digit, index) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.textContent = String(digit);
      btn.style.border = "1px solid #cbd5e1";
      btn.style.borderRadius = "8px";
      btn.style.padding = "10px 0";
      btn.style.cursor = "pointer";
      btn.style.fontWeight = "600";
      btn.onclick = () => {
        if (selectedPositions.length >= 6) return;
        selectedPositions.push(index);
        renderSelected();
      };
      keypad.appendChild(btn);
    });

    const errorText = document.createElement("p");
    errorText.style.minHeight = "18px";
    errorText.style.margin = "0 0 8px 0";
    errorText.style.fontSize = "12px";
    errorText.style.color = "#dc2626";

    const actions = document.createElement("div");
    actions.style.display = "flex";
    actions.style.justifyContent = "space-between";
    actions.style.gap = "8px";

    const left = document.createElement("div");
    left.style.display = "flex";
    left.style.gap = "8px";
    const clearBtn = document.createElement("button");
    clearBtn.type = "button";
    clearBtn.textContent = "Clear";
    clearBtn.style.border = "1px solid #cbd5e1";
    clearBtn.style.borderRadius = "8px";
    clearBtn.style.padding = "8px 10px";
    clearBtn.onclick = () => {
      selectedPositions.length = 0;
      renderSelected();
    };

    const backBtn = document.createElement("button");
    backBtn.type = "button";
    backBtn.textContent = "Backspace";
    backBtn.style.border = "1px solid #cbd5e1";
    backBtn.style.borderRadius = "8px";
    backBtn.style.padding = "8px 10px";
    backBtn.onclick = () => {
      selectedPositions.pop();
      renderSelected();
    };
    left.appendChild(clearBtn);
    left.appendChild(backBtn);

    const right = document.createElement("div");
    right.style.display = "flex";
    right.style.gap = "8px";
    const cancelBtn = document.createElement("button");
    cancelBtn.type = "button";
    cancelBtn.textContent = "Cancel";
    cancelBtn.style.border = "1px solid #cbd5e1";
    cancelBtn.style.borderRadius = "8px";
    cancelBtn.style.padding = "8px 10px";
    cancelBtn.onclick = cancel;

    const submitBtn = document.createElement("button");
    submitBtn.type = "button";
    submitBtn.textContent = "Verify";
    submitBtn.style.border = "none";
    submitBtn.style.background = "#4f46e5";
    submitBtn.style.color = "#fff";
    submitBtn.style.borderRadius = "8px";
    submitBtn.style.padding = "8px 12px";
    submitBtn.onclick = submit;
    right.appendChild(cancelBtn);
    right.appendChild(submitBtn);

    actions.appendChild(left);
    actions.appendChild(right);

    modal.appendChild(title);
    modal.appendChild(subtitle);
    modal.appendChild(selectedBox);
    modal.appendChild(keypad);
    modal.appendChild(errorText);
    modal.appendChild(actions);
    overlay.appendChild(modal);
    document.body.appendChild(overlay);
  });

export const buildHighRiskHeaders = async (action) => {
  const challengeRes = await aprilAPI.requestHighRiskOtp();
  const challenge = challengeRes.data.challenge;
  const positions = await collectVirtualOtpPositions(challenge, action);

  const securityPayload = {
    action,
    ts: new Date().toISOString(),
  };
  let signRes;
  try {
    signRes = await aprilAPI.signPayload(securityPayload);
  } catch (err) {
    const detail = String(err?.response?.data?.detail || err?.message || "").toLowerCase();
    if (detail.includes("private key not found")) {
      // First secure action for this user: provision keys and retry.
      await aprilAPI.rotateKeys();
      signRes = await aprilAPI.signPayload(securityPayload);
    } else {
      throw err;
    }
  }
  const signature = signRes.data.signature_b64;

  return {
    "X-Security-Payload": JSON.stringify(securityPayload),
    "X-Security-Signature": signature,
    "X-OTP-Challenge-ID": challenge.challenge_id,
    "X-OTP-Positions": positions,
  };
};

export const buildOtpOnlyHeaders = async () => {
  const challengeRes = await aprilAPI.requestHighRiskOtp();
  const challenge = challengeRes.data.challenge;
  const positions = await collectVirtualOtpPositions(challenge, "OTP verification");
  return {
    "X-OTP-Challenge-ID": challenge.challenge_id,
    "X-OTP-Positions": positions,
  };
};

export default api;
