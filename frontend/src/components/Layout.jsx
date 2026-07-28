import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useState } from "react";
import { useAuth } from "../auth/AuthContext";
import "../style/Layout.css";

const links = [
  ["/","Dashboard","◇"],["/tools","Tools","⚡"],["/tools/lead-generation","Lead Generation","✦"],
  ["/tools/spreadsheet-enrichment","Spreadsheet Enrichment","▦"],["/projects","Projects","▣"],
  ["/jobs","Jobs","◉"],["/settings","Settings","⚙"],["/contact","Contact","✉"],
  ["/request-tool","Request Tool","＋"],["/about","About","ⓘ"],
];

export default function Layout() {
  const { user, logout } = useAuth(); const navigate = useNavigate(); const [open,setOpen]=useState(false);
  function signOut(){logout();navigate("/login");}
  return <div className="app-shell">
    <button className="mobile-menu-button" aria-expanded={open} onClick={()=>setOpen(!open)}>☰</button>
    <aside className={`sidebar ${open?"open":""}`}>
      <div className="brand"><div className="brand-icon">◈</div><span>AutoLead</span></div>
      <nav className="main-navigation">{links.map(([to,label,icon])=><NavLink key={to} to={to} end={to==="/"} className="nav-item" onClick={()=>setOpen(false)}><span>{icon}</span>{label}</NavLink>)}
        {user?.is_admin&&<NavLink to="/admin" className="nav-item"><span>◆</span>Admin Dashboard</NavLink>}</nav>
      <div className="sidebar-bottom"><button className="nav-item logout-button" onClick={signOut}><span>↪</span>Logout</button>
        <div className="user-profile"><div className="user-avatar">{user?.name?.[0]?.toUpperCase()}</div>
          <div className="user-info"><strong>{user?.name}</strong><span>{user?.is_admin?"Administrator":"User"}</span></div></div></div>
    </aside>
    <main className="main-area"><header className="top-header"><div className="breadcrumb">AutoLead</div>
      <div className="header-user"><div className="small-avatar">{user?.name?.[0]?.toUpperCase()}</div><span>{user?.name}</span></div></header>
      <section className="page-content"><Outlet/></section></main>
  </div>;
}
