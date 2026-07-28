import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api, { apiError } from "../api/client";

export default function Register() {
    const [form, setForm] = useState({ name:"",email:"",password:"",confirm:"" });
    const [busy,setBusy]=useState(false); const [error,setError]=useState(""); const navigate=useNavigate();
    async function submit(event) { event.preventDefault(); if (busy) return;
        if (form.password !== form.confirm) return setError("Passwords do not match.");
        try { setBusy(true); setError(""); await api.post("/auth/register",{name:form.name,email:form.email,password:form.password}); navigate("/login"); }
        catch(err){setError(apiError(err,"Unable to register."));} finally{setBusy(false);}
    }
    return <main className="auth-page"><form className="glass-card auth-card" onSubmit={submit}>
        <div className="eyebrow">AUTOLEAD / REGISTER</div><h1>Create your account.</h1>
        <label>Name</label><input required value={form.name} onChange={(e)=>setForm({...form,name:e.target.value})}/>
        <label>Email</label><input type="email" required value={form.email} onChange={(e)=>setForm({...form,email:e.target.value})}/>
        <label>Password</label><input type="password" minLength="8" required value={form.password} onChange={(e)=>setForm({...form,password:e.target.value})}/>
        <label>Confirm password</label><input type="password" required value={form.confirm} onChange={(e)=>setForm({...form,confirm:e.target.value})}/>
        {error&&<p className="error-message">{error}</p>}<button className="crystal-button" disabled={busy}>{busy?"Creating...":"Register"}</button>
        <p>Already registered? <Link to="/login">Sign in</Link></p></form></main>;
}
