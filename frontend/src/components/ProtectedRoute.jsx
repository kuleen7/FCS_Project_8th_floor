import { Navigate, useLocation } from "react-router-dom";
import Layout from "./Layout";

function ProtectedRoute() {
  const location = useLocation();
  const token = localStorage.getItem("token");

  if (!token) {
    return (
      <Navigate
        to="/login"
        replace
        state={{ from: location }}
      />
    );
  }

  return <Layout />;
}

export default ProtectedRoute;

