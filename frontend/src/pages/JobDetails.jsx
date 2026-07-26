/* eslint-disable react-hooks/set-state-in-effect */
import { Link, useParams } from "react-router-dom";
import { useCallback, useEffect, useState } from "react";
import api, { apiError } from "../api/client";

function JobDetails() {
    const { jobId } = useParams();
    const [job, setJob] = useState(null);
    const [companies, setCompanies] = useState([]);
    const [companyPage, setCompanyPage] = useState(1);
    const [companyTotal, setCompanyTotal] = useState(0);
    const [companyPages, setCompanyPages] = useState(0);
    const [progress, setProgress] = useState(null);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [enriching, setEnriching] = useState(false);
    const [notice, setNotice] = useState("");
    const [error, setError] = useState("");

    const fetchCompanies = useCallback(async () => {
        const { data } = await api.get(`/jobs/${jobId}/companies?page=${companyPage}&limit=9`);
        setCompanies(data.companies); setCompanyTotal(data.total); setCompanyPages(data.total_pages);
    }, [jobId, companyPage]);

    const load = useCallback(async () => {
        try {
            setError("");
            const [{ data }] = await Promise.all([
                api.get(`/jobs/${jobId}`), fetchCompanies(),
            ]);
            setJob(data);
            if (data.status === "completed") {
                const response = await api.get(`/jobs/${jobId}/enrichment-progress`);
                setProgress(response.data);
            }
        } catch (err) {
            setError(apiError(err, "Unable to load job details."));
        } finally {
            setLoading(false);
        }
    }, [jobId, fetchCompanies]);

    useEffect(() => { load(); }, [load]);

    async function refreshJob() {
        try {
            setRefreshing(true); setError("");
            const { data } = await api.post(`/jobs/${jobId}/refresh`);
            setNotice(data.status === "completed" ? `${data.companies_saved} new companies saved.` : "Firecrawl is still processing.");
            await load();
        } catch (err) { setError(apiError(err, "Unable to refresh this job.")); }
        finally { setRefreshing(false); }
    }

    async function enrich() {
        try {
            setEnriching(true); setError("");
            const { data } = await api.post(`/jobs/${jobId}/enrich?limit=5`);
            setNotice(`Enrichment processed ${data.processed}; ${data.remaining} remain.`);
            await load();
        } catch (err) { setError(apiError(err, "Unable to enrich companies.")); }
        finally { setEnriching(false); }
    }

    if (loading) return <main className="job-details-page"><div className="eyebrow">AUTOLEAD / JOB</div><h1>Loading job...</h1></main>;
    if (!job) return <main className="job-details-page"><h1>Job not found</h1><p className="error-message">{error}</p><Link to="/jobs">← Back to Jobs</Link></main>;

    return (
        <main className="job-details-page">
            <Link to="/jobs" className="back-link">← Back to Jobs</Link>
            <div className="job-details-header"><div><div className="eyebrow">AUTOLEAD / JOB</div><h1>Job #{job.id}</h1>
                <p>{job.country}{job.province ? ` · ${job.province}` : ""}</p></div>
                <div className="job-detail-actions">
                    {job.status !== "completed" && <button className="crystal-button" onClick={refreshJob} disabled={refreshing}>{refreshing ? "Refreshing..." : "Refresh Status"}</button>}
                    {job.status === "completed" && companyTotal > 0 && <button className="crystal-button" onClick={enrich} disabled={enriching}>{enriching ? "Enriching..." : "Enrich Missing Social Links"}</button>}
                    <span className={`job-status-badge ${job.status}`}>{job.status}</span>
                </div>
            </div>
            {error && <p className="error-message">{error}</p>}{notice && <div className="glass-card refresh-summary">{notice}</div>}
            {job.firecrawl_error && <div className="job-error">{job.firecrawl_error}</div>}
            <section className="firecrawl-timeline glass-card">
                <div className="timeline-step completed">Job created</div>
                <div className={`timeline-step ${job.firecrawl_status === "processing" ? "processing" : job.firecrawl_status}`}>Firecrawl {job.firecrawl_status}</div>
                <div className={`timeline-step ${job.status}`}>Results {job.status}</div>
            </section>
            <section className="job-info-grid">
                <div className="glass-card job-info-card"><span>Industries</span><strong>{job.industries.join(", ")}</strong></div>
                <div className="glass-card job-info-card"><span>Target Leads</span><strong>{job.lead_count}</strong></div>
                <div className="glass-card job-info-card"><span>Companies Found</span><strong>{companyTotal}</strong></div>
            </section>
            {progress && <div className="glass-card enrichment-progress">Enrichment: {progress.completed} completed · {progress.pending} pending · {progress.failed} failed · {progress.skipped} skipped</div>}
            <section className="companies-section"><div className="section-header"><div><div className="eyebrow">RESULTS</div><h2>Companies</h2>
                <p>Businesses discovered by this lead generation job.</p></div></div>
                <div className="companies-grid">{companies.map((company) => (
                    <div key={company.id} className="company-card glass-card">
                        <div className="company-card-header"><div className="company-symbol">{company.company_name?.charAt(0).toUpperCase()}</div>
                            <div><h3>{company.company_name}</h3><span>{company.industry}</span></div>
                            <span className={`enrichment-badge ${company.enrichment_status}`}>{company.enrichment_status}</span></div>
                        <div className="company-details">{company.email && <p>✉ {company.email}</p>}{company.phone && <p>☎ {company.phone}</p>}
                            {company.headquarters && <p>Location: {company.headquarters}</p>}</div>
                        <div className="company-actions">{["website", "linkedin", "facebook", "instagram"].map((field) => company[field] && (
                            <a key={field} href={company[field]} target="_blank" rel="noreferrer" className="company-action-button">{field[0].toUpperCase() + field.slice(1)}</a>
                        ))}</div>
                    </div>
                ))}</div>
                {companyPages > 1 && <div className="pagination"><button className="pagination-button" disabled={companyPage === 1} onClick={() => setCompanyPage((p) => p - 1)}>← Previous</button>
                    <span>Page {companyPage} of {companyPages}</span><button className="pagination-button" disabled={companyPage === companyPages} onClick={() => setCompanyPage((p) => p + 1)}>Next →</button></div>}
            </section>
        </main>
    );
}

export default JobDetails;
