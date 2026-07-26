import axios from "axios";

export const API_BASE_URL =
    import.meta.env.VITE_API_URL || "http://localhost:8000";

const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 90000,
});

export function apiError(error, fallback = "Something went wrong.") {
    if (error.code === "ECONNABORTED") {
        return "The server is taking longer than expected. Render may be waking up; please try again.";
    }
    return error.response?.data?.detail || error.response?.data?.message || error.message || fallback;
}

export default api;
