import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api, { apiError } from "../api/client";
import { useAuth } from "../auth/AuthContext";

export default function Login() {
    const [form, setForm] = useState({ email: "", password: "" });
    const [busy, setBusy] = useState(false); const [error, setError] = useState("");
    const { login } = useAuth(); const navigate = useNavigate();
    async function submit(event) {
        event.preventDefault(); if (busy) return;
        try { setBusy(true); setError(""); const { data } = await api.post("/auth/login", form);
            login(data.access_token, data.user); navigate("/"); }
        catch (err) { setError(apiError(err, "Unable to sign in.")); } finally { setBusy(false); }
    }
    return <main className="auth-page"><form className="glass-card auth-card" onSubmit={submit}>
        <div className="eyebrow">AUTOLEAD / LOGIN</div><h1>Welcome back.</h1>
        <label>Email</label><input type="email" required value={form.email} onChange={(e) => setForm({...form,email:e.target.value})}/>
        <label>Password</label><input type="password" required value={form.password} onChange={(e) => setForm({...form,password:e.target.value})}/>
        {error && <p className="error-message">{error}</p>}<button className="crystal-button" disabled={busy}>{busy ? "Signing in..." : "Sign In"}</button>
        <p>New here? <Link to="/register">Create an account</Link></p></form></main>;
}
