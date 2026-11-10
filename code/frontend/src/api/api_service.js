import axios from "axios";

const api_service = axios.create({
  baseURL: "http://localhost:8000",
  withCredentials: true, 
});

api_service.interceptors.response.use(
  (res) => res,
  (err) => {
    const url = err.config?.url || "";
    const isAuthCall = url.includes("/user/login") || url.includes("/user/me");
    if (err.response?.status === 401 && !isAuthCall) {
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export default api_service;
