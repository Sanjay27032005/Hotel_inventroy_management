import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Spinner } from "./ui";

export default function ProtectedRoute({ children, requireRoles }) {
  const { user, loading, isStaff } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-linen-100">
        <Spinner />
      </div>
    );
  }

  if (!user || !isStaff) {
    return <Navigate to="/portal/login" state={{ from: location }} replace />;
  }

  if (requireRoles && !requireRoles.includes(user.role)) {
    return (
      <div className="flex min-h-[60vh] flex-col items-center justify-center text-center">
        <p className="font-display text-xl text-ink-900">You don't have access to this page</p>
        <p className="mt-2 text-sm text-ink-700/70">
          Your role ({user.role.replace(/_/g, " ")}) doesn't include this module.
        </p>
      </div>
    );
  }

  return children;
}
