import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "./AuthContext";
import LoadingScreen from "../components/LoadingScreen";

export default function ProtectedRoute({ admin = false }) {
    const { user, loading } = useAuth();
    if (loading) return <main className="dashboard-page"><LoadingScreen /></main>;
    if (!user) return <Navigate to="/login" replace />;
    if (admin && !user.is_admin) return <Navigate to="/" replace />;
    return <Outlet />;
}
