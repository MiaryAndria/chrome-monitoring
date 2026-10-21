import { useEffect, useState } from "react";
import { Navigate, Outlet } from "react-router-dom";
import { GetMe } from "../fonction/userFonction";

export default function ProtectedRoute() {
  const [status, setStatus] = useState("loading");

  useEffect(() => {
    GetMe()
      .then(() => setStatus("ok"))
      .catch(() => setStatus("denied"));
  }, []);

  if (status === "loading") return null; // ou un spinner
  if (status === "denied") return <Navigate to="/login" replace />;
  return <Outlet />;
}