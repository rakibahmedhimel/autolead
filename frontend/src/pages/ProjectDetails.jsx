/* eslint-disable react-hooks/set-state-in-effect */
import { Link, useParams } from "react-router-dom";
import { useCallback, useEffect, useState } from "react";
import api, { apiError } from "../api/client";
import LoadingScreen from "../components/LoadingScreen";
import CompanyResults, { downloadCompaniesCsv } from "../components/CompanyResults";
import Toast from "../components/Toast";

export default function ProjectDetails() {
  const { projectId } = useParams();
  const [project,setProject]=useState(null),[jobs,setJobs]=useState([]),[companies,setCompanies]=useState([]);
  const [jobsPage,setJobsPage]=useState(1),[companyPage,setCompanyPage]=useState(1),[jobsPages,setJobsPages]=useState(0),[companyPages,setCompanyPages]=useState(0);
  const [jobsTotal,setJobsTotal]=useState(0),[companyTotal,setCompanyTotal]=useState(0),[loading,setLoading]=useState(true),[downloading,setDownloading]=useState(false);
  const [error,setError]=useState(""),[toast,setToast]=useState(null);
  const loadProject=useCallback(async()=>{try{const{data}=await api.get(`/projects/${projectId}`);setProject(data);}catch(e){setError(apiError(e,"Unable to load project."));}finally{setLoading(false)}},[projectId]);
  const loadJobs=useCallback(async()=>{const{data}=await api.get(`/projects/${projectId}/jobs?page=${jobsPage}&limit=10`);setJobs(data.jobs);setJobsPages(data.total_pages);setJobsTotal(data.total)},[projectId,jobsPage]);
  const loadCompanies=useCallback(async()=>{const{data}=await api.get(`/projects/${projectId}/companies?page=${companyPage}&limit=10`);setCompanies(data.companies);setCompanyPages(data.total_pages);setCompanyTotal(data.total)},[projectId,companyPage]);
  useEffect(()=>{loadProject();},[loadProject]); useEffect(()=>{loadJobs().catch(()=>setError("Unable to load project jobs."));},[loadJobs]); useEffect(()=>{loadCompanies().catch(()=>setError("Unable to load companies."));},[loadCompanies]);
  async function refresh(){try{setLoading(true);await Promise.all([loadProject(),loadJobs(),loadCompanies()]);setToast({title:"Project data refreshed."});}catch(e){setToast({type:"error",title:"Refresh failed",body:apiError(e)});}finally{setLoading(false)}}
  async function download(){try{setDownloading(true);const rows=[];let page=1,pages=1;do{const{data}=await api.get(`/projects/${projectId}/companies?page=${page}&limit=100`);rows.push(...data.companies);pages=data.total_pages;page+=1;}while(page<=pages);
    downloadCompaniesCsv(rows,`AutoLead_Project_${project.name.replace(/[^a-z0-9]+/gi,"_")}_Companies.csv`);setToast({title:"Download ready",body:`Exported ${rows.length} companies.`});}catch(e){setToast({type:"error",title:"Download failed",body:apiError(e)});}finally{setDownloading(false)}}
  if(loading&&!project)return <main className="project-details-page"><LoadingScreen /></main>;
  if(!project)return <main className="project-details-page"><h1>Project not found</h1><p className="error-message">{error}</p><Link to="/projects">← Back to Projects</Link></main>;
  return <main className="project-details-page"><Link to="/projects" className="back-link">← Back to Projects</Link>
    <div className="project-details-header"><div><div className="eyebrow">AUTOLEAD / PROJECT</div><h1>{project.name}</h1><p>{project.description||"No description provided."}</p></div>
      <div className="job-detail-actions"><button className="secondary-button" disabled={loading} onClick={refresh}>{loading?"Refreshing...":"Refresh"}</button><Link to={`/tools/lead-generation?projectId=${project.id}`} className="crystal-button">+ New Lead Job</Link></div></div>
    {error&&<p className="error-message">{error}</p>}<section className="project-stats">{[["Project ID",`#${project.id}`],["Created",new Date(project.created_at).toLocaleDateString()],["Jobs",jobsTotal],["Companies",companyTotal]].map(([l,v])=><div className="glass-card project-stat-card" key={l}><span>{l}</span><strong>{v}</strong></div>)}</section>
    <section className="project-section"><div className="section-header"><div><div className="eyebrow">PROJECT ACTIVITY</div><h2>Lead Generation Jobs</h2></div></div><div className="project-jobs-list">
      {!jobs.length&&<div className="glass-card empty-state"><h3>No jobs yet</h3><p>Start a lead generation job for this project.</p></div>}
      {jobs.map(j=><Link key={j.id} to={`/projects/${projectId}/jobs/${j.id}`} className="project-job-row glass-card"><div><span className="job-card-id">JOB #{j.id}</span><h3>{j.country}{j.province?` · ${j.province}`:""}</h3></div><div className="project-job-meta"><span>{j.industries.join(", ")}</span><span>{j.lead_count} target leads</span></div><span className={`job-status-badge ${j.status}`}>{j.status}</span></Link>)}</div>
      {jobsPages>1&&<div className="pagination"><button className="pagination-button" disabled={jobsPage===1} onClick={()=>setJobsPage(p=>p-1)}>← Previous</button><span>Page {jobsPage} of {jobsPages}</span><button className="pagination-button" disabled={jobsPage===jobsPages} onClick={()=>setJobsPage(p=>p+1)}>Next →</button></div>}</section>
    <div className="results-actions"><button className="secondary-button" disabled={downloading||!companyTotal} onClick={download}>{downloading?"Preparing Sheet...":"Download Sheet"}</button></div>
    <CompanyResults companies={companies} total={companyTotal} page={companyPage} totalPages={companyPages} onPageChange={setCompanyPage} title="Collected Companies" />
    <Toast toast={toast} onClose={()=>setToast(null)}/></main>;
}
