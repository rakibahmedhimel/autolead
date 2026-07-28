/* eslint-disable react-hooks/set-state-in-effect */
import { Link } from "react-router-dom";
import { useCallback, useEffect, useRef, useState } from "react";
import api, { apiError } from "../api/client";
import LoadingScreen from "../components/LoadingScreen";
import Toast from "../components/Toast";

export default function Projects() {
  const [projects, setProjects] = useState([]), [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false), [name, setName] = useState(""), [description, setDescription] = useState("");
  const [creating, setCreating] = useState(false), [error, setError] = useState(""), [toast, setToast] = useState(null);
  const guard = useRef(false);
  const load = useCallback(async () => { try { setError(""); const { data } = await api.get("/projects/"); setProjects(data); }
    catch (err) { setError(apiError(err, "Unable to load projects.")); } finally { setLoading(false); } }, []);
  useEffect(() => { load(); }, [load]);
  useEffect(() => { const key = (e) => e.key === "Escape" && !creating && setOpen(false); window.addEventListener("keydown", key); return () => window.removeEventListener("keydown", key); }, [creating]);
  async function create(e) { e.preventDefault(); if (!name.trim() || guard.current) return; guard.current = true; setCreating(true);
    try { await api.post("/projects/", { name: name.trim(), description: description.trim() || null }); setOpen(false); setName(""); setDescription(""); await load(); setToast({ title: "Project created", body: "The project is ready for lead generation." }); }
    catch (err) { setError(apiError(err, "Unable to create project.")); } finally { guard.current = false; setCreating(false); } }
  if (loading) return <main className="projects-page"><LoadingScreen /></main>;
  return <main className="projects-page"><div className="page-header"><div><div className="eyebrow">AUTOLEAD / WORKSPACE</div><h1>Your <span>Projects</span></h1>
    <p>Organize your lead generation jobs and collected business data.</p></div><button className="crystal-button" onClick={() => { setError(""); setOpen(true); }}>+ New Project</button></div>
    {error && !open && <p className="error-message">{error}</p>}<section className="projects-grid">{projects.map((project) => <Link key={project.id} to={`/projects/${project.id}`} className="project-card glass-card">
      <div className="project-card-top"><div className="project-symbol">{project.name.slice(0,2).toUpperCase()}</div><span className="status-badge">Active</span></div>
      <h2>{project.name}</h2><p>{project.description || "No description provided."}</p><div className="project-meta"><span>Project #{project.id}</span><span>{new Date(project.created_at).toLocaleDateString()}</span></div></Link>)}
      <button className="project-card glass-card create-project-card" onClick={() => { setError(""); setOpen(true); }}><div className="create-project-icon">+</div><h2>Create a new project</h2><p>Start organizing a new lead generation campaign.</p></button></section>
    {open && <div className="modal-overlay" onClick={() => !creating && setOpen(false)}><div className="project-modal glass-card" onClick={(e) => e.stopPropagation()}>
      <div className="modal-header"><div><div className="eyebrow">AUTOLEAD / PROJECT</div><h2>Create New Project</h2></div><button className="modal-close" onClick={() => setOpen(false)} aria-label="Close">×</button></div>
      <form onSubmit={create}><div className="form-group"><label>Project name</label><input autoFocus required value={name} onChange={(e) => setName(e.target.value)} /></div>
        <div className="form-group"><label>Optional description</label><textarea value={description} onChange={(e) => setDescription(e.target.value)} /></div>{error && <p className="error-message">{error}</p>}
        <div className="modal-actions"><button type="button" className="secondary-button" disabled={creating} onClick={() => setOpen(false)}>Cancel</button><button className="crystal-button" disabled={creating || !name.trim()}>{creating ? "Creating..." : "Create Project"}</button></div></form></div></div>}
    <Toast toast={toast} onClose={() => setToast(null)} /></main>;
}
