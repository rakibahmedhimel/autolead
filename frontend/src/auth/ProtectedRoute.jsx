import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "./AuthContext";

export default function ProtectedRoute({ admin = false }) {
    const { user, loading } = useAuth();
    if (loading) return <main className="dashboard-page"><h1>Loading...</h1></main>;
    if (!user) return <Navigate to="/login" replace />;
    if (admin && !user.is_admin) return <Navigate to="/" replace />;
    return <Outlet />;
}
