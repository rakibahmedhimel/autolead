/* eslint-disable react-hooks/set-state-in-effect */
import { Link, useParams } from "react-router-dom";
import { useCallback, useEffect, useState } from "react";
import api, { apiError } from "../api/client";
import LoadingScreen from "../components/LoadingScreen";
import CompanyResults, { downloadCompaniesCsv } from "../components/CompanyResults";
import Toast from "../components/Toast";

export default function JobDetails(){
 const{jobId,projectId}=useParams(),[job,setJob]=useState(null),[companies,setCompanies]=useState([]),[page,setPage]=useState(1),[total,setTotal]=useState(0),[pages,setPages]=useState(0),[progress,setProgress]=useState(null);
 const[loading,setLoading]=useState(true),[refreshing,setRefreshing]=useState(false),[enriching,setEnriching]=useState(false),[downloading,setDownloading]=useState(false),[error,setError]=useState(""),[toast,setToast]=useState(null);
 const loadCompanies=useCallback(async()=>{const{data}=await api.get(`/jobs/${jobId}/companies?page=${page}&limit=10`);setCompanies(data.companies);setTotal(data.total);setPages(data.total_pages)},[jobId,page]);
 const load=useCallback(async()=>{try{setError("");const[{data}]=await Promise.all([api.get(`/jobs/${jobId}`),loadCompanies()]);setJob(data);if(data.status==="completed"){try{const p=await api.get(`/jobs/${jobId}/enrichment-progress`);setProgress(p.data)}catch{/* progress is optional */}}}catch(e){setError(apiError(e,"Unable to load job details."));}finally{setLoading(false)}},[jobId,loadCompanies]);
 useEffect(()=>{load();},[load]);
 async function refresh(){try{setRefreshing(true);const{data}=await api.post(`/jobs/${jobId}/refresh`);await load();setToast({title:"Job status refreshed.",body:`Latest status: ${data.status||data.firecrawl_status||"updated"}.`});}catch(e){setToast({type:"error",title:"Refresh failed",body:apiError(e)});}finally{setRefreshing(false)}}
 async function enrich(){try{setEnriching(true);const{data}=await api.post(`/jobs/${jobId}/enrich?limit=5`);await load();const done=data.processed??data.completed??0,remaining=data.remaining??0;setToast({title:"Enrichment updated",body:`${done} companies enriched · ${remaining} remaining`});}catch(e){setToast({type:"error",title:"Enrichment failed",body:apiError(e)});}finally{setEnriching(false)}}
 async function download(){try{setDownloading(true);const rows=[];let current=1,last=1;do{const{data}=await api.get(`/jobs/${jobId}/companies?page=${current}&limit=100`);rows.push(...data.companies);last=data.total_pages;current+=1;}while(current<=last);downloadCompaniesCsv(rows,`AutoLead_Job_${jobId}_Companies.csv`);setToast({title:"Download ready",body:`Exported ${rows.length} companies.`});}catch(e){setToast({type:"error",title:"Download failed",body:apiError(e)});}finally{setDownloading(false)}}
 if(loading)return <main className="job-details-page"><LoadingScreen/></main>;if(!job)return <main className="job-details-page"><h1>Job not found</h1><p className="error-message">{error}</p></main>;
 const retry=(progress?.failed||0)>0||((progress?.pending||0)>0&&(progress?.processing||0)===0);
 return <main className="job-details-page"><Link to={projectId?`/projects/${projectId}`:"/jobs"} className="back-link">← Back to {projectId?"Project":"Jobs"}</Link>
  <div className="job-details-header"><div><div className="eyebrow">AUTOLEAD / JOB</div><h1>Job #{job.id}</h1><p>{job.country}{job.province?` · ${job.province}`:""}</p></div><div className="job-detail-actions">
   {job.status!=="completed"&&<button className="crystal-button" onClick={refresh} disabled={refreshing}>{refreshing?"Refreshing...":"Refresh Status"}</button>}
   {retry&&<button className="secondary-button" onClick={enrich} disabled={enriching}>{enriching?"Retrying...":"Retry Unfinished Enrichment"}</button>}
   <button className="secondary-button" onClick={download} disabled={downloading||!total}>{downloading?"Preparing Sheet...":"Download Sheet"}</button><span className={`job-status-badge ${job.status}`}>{job.status}</span></div></div>
  {error&&<p className="error-message">{error}</p>}{job.firecrawl_error&&<div className="job-error">{job.firecrawl_error}</div>}
  <section className="firecrawl-timeline glass-card"><div className="timeline-step completed">Job created</div><div className={`timeline-step ${job.firecrawl_status}`}>Firecrawl {job.firecrawl_status}</div><div className={`timeline-step ${job.status}`}>Results {job.status}</div></section>
  <section className="job-info-grid"><div className="glass-card job-info-card"><span>Industries</span><strong>{job.industries.join(", ")}</strong></div><div className="glass-card job-info-card"><span>Target Leads</span><strong>{job.lead_count}</strong></div><div className="glass-card job-info-card"><span>Companies Found</span><strong>{total}</strong></div></section>
  <CompanyResults companies={companies} total={total} page={page} totalPages={pages} onPageChange={setPage} progress={progress}/><Toast toast={toast} onClose={()=>setToast(null)}/></main>
}
