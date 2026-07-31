import axios from "axios";

// Points at the FastAPI backend. Override with a .env file
// (VITE_API_BASE_URL=https://your-api.com) for non-local setups.
const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const API = axios.create({
  baseURL: BASE_URL,
});

API.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

// If the token has expired/is invalid, the backend returns 401.
// Clear local session and bounce to login rather than showing a dead UI.
API.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");

      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }

    return Promise.reject(error);
  }
);

/* ---------------------------------- Auth --------------------------------- */

export const login = (data) => API.post("/auth/login", data);

export const register = (data) => API.post("/auth/register", data);

export function saveSession(tokenResponse) {
  localStorage.setItem("token", tokenResponse.access_token);
  localStorage.setItem("user", JSON.stringify(tokenResponse.user));
}

export function getSessionUser() {
  const raw = localStorage.getItem("user");
  return raw ? JSON.parse(raw) : null;
}

export function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
}

/* -------------------------------- Folders --------------------------------- */

export const getFolders = () => API.get("/folders/");

export const createFolder = (data) => API.post("/folders/", data);

export const updateFolder = (id, data) => API.put(`/folders/${id}`, data);

export const deleteFolder = (id) => API.delete(`/folders/${id}`);

/* ------------------------------- Documents --------------------------------- */

export const getDocuments = () => API.get("/documents/");

export const getRecentDocuments = () => API.get("/documents/recent");

export const getDocument = (id) => API.get(`/documents/${id}`);

export const getDocumentText = (id) => API.get(`/documents/${id}/text`);

export const uploadPDF = (formData) =>
  API.post("/documents/upload", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

export const deleteDocument = (id) => API.delete(`/documents/${id}`);

export const moveDocument = (id, folderId) =>
  API.put(`/documents/${id}/move`, { folder_id: folderId });

export function getDocumentFileUrl(doc) {
  if (!doc?.file_url) return null;
  return `${BASE_URL}${doc.file_url}`;
}

/* ------------------------------- Study Tools ------------------------------- */

export const getSummary = (id) => API.get(`/documents/${id}/summary`);

export const generateSummary = (id, options = {}) =>
  API.post(`/documents/${id}/summary`, options);

export const getFlashcards = (id) => API.get(`/documents/${id}/flashcards`);

export const generateFlashcards = (id, options = {}) =>
  API.post(`/documents/${id}/flashcards`, options);

export const getQuiz = (id) => API.get(`/documents/${id}/quiz`);

export const generateQuiz = (id, options = {}) =>
  API.post(`/documents/${id}/quiz`, options);

/* --------------------------------- Mentor ---------------------------------- */

export const getDailyMentorBriefing = () => API.get("/mentor/daily");

/* --------------------------------- Planner --------------------------------- */

export const getTodayTasks = () => API.get("/planner/tasks/today");
export const createTask = (title) => API.post("/planner/tasks", { title });
export const toggleTask = (id) => API.patch(`/planner/tasks/${id}/toggle`);
export const deleteTask = (id) => API.delete(`/planner/tasks/${id}`);

export const getAssignments = () => API.get("/planner/assignments");
export const createAssignment = (data) => API.post("/planner/assignments", data);
export const completeAssignment = (id) =>
  API.patch(`/planner/assignments/${id}/complete`);
export const deleteAssignment = (id) => API.delete(`/planner/assignments/${id}`);

export const getDeadlines = () => API.get("/planner/deadlines");
export const createDeadline = (data) => API.post("/planner/deadlines", data);
export const deleteDeadline = (id) => API.delete(`/planner/deadlines/${id}`);

/* ----------------------------- Planner Attachments -------------------------- */
// Attach files (assignment briefs, rubrics, notes) to a task or assignment.
// The mentor reads whatever text can be extracted from these to ground its
// recommendations in the file's actual content.

export const uploadTaskAttachment = (taskId, file) => {
  const formData = new FormData();
  formData.append("file", file);
  return API.post(`/planner/tasks/${taskId}/attachments`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const uploadAssignmentAttachment = (assignmentId, file) => {
  const formData = new FormData();
  formData.append("file", file);
  return API.post(
    `/planner/assignments/${assignmentId}/attachments`,
    formData,
    { headers: { "Content-Type": "multipart/form-data" } }
  );
};

export const deleteAttachment = (attachmentId) =>
  API.delete(`/planner/attachments/${attachmentId}`);

export default API;
