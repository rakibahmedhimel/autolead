import axios from "axios";

export const API_BASE_URL =
    import.meta.env.VITE_API_URL || "http://localhost:8000";

const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 90000,
});

api.interceptors.request.use((config) => {
    const token = localStorage.getItem("autolead_token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
});

api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401 && !error.config?.url?.includes("/auth/login")) {
            localStorage.removeItem("autolead_token");
            sessionStorage.clear();
            if (window.location.pathname !== "/login") window.location.assign("/login");
        }
        return Promise.reject(error);
    },
);

export function apiError(error, fallback = "Something went wrong.") {
    if (error.code === "ECONNABORTED") {
        return "The server is taking longer than expected; please try again.";
    }
    const status = error.response?.status;
    const detail = error.response?.data?.detail;
    if (typeof detail === "object" && detail?.message) return detail.message;
    if (detail) return detail;
    const messages = {
        401: "Your session has expired. Please sign in again.",
        403: "You do not have permission to perform this action.",
        404: "The requested resource was not found.",
        409: "This record already exists.",
        422: "Please check the submitted information.",
        429: "Too many requests. Please wait and try again.",
        500: "The server encountered an error. Please try again.",
    };
    return messages[status] || error.response?.data?.message || error.message || fallback;
}

export default api;
