import { useEffect, useState } from "react";
import { Navigate, Outlet } from "react-router-dom";
import { GetMe } from "../fonction/userFonction";

export default function PublicRoute() {
  const [status, setStatus] = useState("loading");

  useEffect(() => {
    GetMe()
      .then(() => setStatus("logged"))
      .catch(() => setStatus("guest"));
  }, []);

  if (status === "loading") return null;
  if (status === "logged") return <Navigate to="/dashboard" replace />;
  return <Outlet />;
}