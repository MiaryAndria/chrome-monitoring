import axios from "axios";

const api_service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api",
  withCredentials: true, // indispensable pour envoyer le cookie
});

api_service.interceptors.response.use(
  (res) => res,
  (err) => {
    const url = err.config?.url || "";
    const isAuthCall = url.includes("/user/login") || url.includes("/user/me");

    // Session expirée pendant l'utilisation → retour au login
    if (err.response?.status === 401 && !isAuthCall) {
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export default api_service;
