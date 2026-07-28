/* eslint-disable react-hooks/set-state-in-effect, react-refresh/only-export-components */
import { createContext, useContext, useEffect, useState } from "react";
import api from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    useEffect(() => {
        if (!localStorage.getItem("autolead_token")) { setLoading(false); return; }
        api.get("/auth/me").then(({ data }) => setUser(data)).catch(() => {
            localStorage.removeItem("autolead_token"); setUser(null);
        }).finally(() => setLoading(false));
    }, []);
    function login(token, currentUser) {
        localStorage.setItem("autolead_token", token); setUser(currentUser);
    }
    function logout() {
        localStorage.removeItem("autolead_token");
        sessionStorage.clear();
        setUser(null);
    }
    return <AuthContext.Provider value={{ user, loading, login, logout }}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);
