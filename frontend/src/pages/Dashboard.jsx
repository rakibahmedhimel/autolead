import { useEffect,useState } from "react"; import { Link } from "react-router-dom"; import api,{apiError} from "../api/client";
export default function Dashboard(){
 const [data,setData]=useState(null),[error,setError]=useState("");
 useEffect(()=>{api.get("/dashboard").then(r=>setData(r.data)).catch(e=>setError(apiError(e)));},[]);
 if(!data)return <main className="dashboard-page"><h1>{error||"Loading dashboard..."}</h1></main>;
 const stats=[["Projects",data.total_projects],["Jobs",data.total_jobs],["Completed",data.completed_jobs],["Processing",data.processing_jobs],["Failed",data.failed_jobs],["Companies",data.companies],["Credits Used",data.credits_used]];
 return <main className="dashboard-page"><header className="dashboard-header"><div className="eyebrow">AUTOLEAD / COMMAND CENTER</div>
  <h1>Welcome, <span>{data.user.name}.</span></h1><p className="dashboard-description">Your real-time workspace activity and lead pipeline.</p></header>
  <section className="project-stats">{stats.map(([label,value])=><div className="glass-card project-stat-card" key={label}><span>{label}</span><strong>{value}</strong></div>)}</section>
  <div className="dashboard-grid"><section className="glass-card generation-card"><h2>Quick actions</h2><div className="active-job-actions">
   <Link className="crystal-button" to="/tools/lead-generation">Start Lead Generation</Link><Link className="secondary-button" to="/tools/spreadsheet-enrichment">Enrich Spreadsheet</Link><Link className="secondary-button" to="/projects">Projects</Link></div></section>
   <section className="glass-card generation-card"><h2>Recent jobs</h2>{data.recent_jobs.length?data.recent_jobs.map(j=><Link key={j.id} to={`/jobs/${j.id}`} className="back-link">Job #{j.id} · {j.status}</Link>):<p>No jobs yet.</p>}</section></div></main>;
}
