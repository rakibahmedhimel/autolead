/* eslint-disable react-hooks/exhaustive-deps */
import { Link } from "react-router-dom";
import { useEffect, useState } from "react";
import api, { apiError } from "../api/client";

function Jobs() {
    const [jobs, setJobs] = useState([]);
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(0);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [summary, setSummary] = useState(null);
    const [error, setError] = useState("");

    useEffect(() => { fetchJobs(); }, [page]);

    async function fetchJobs() {
        try {
            setLoading(true);
            setError("");
            const { data } = await api.get(`/jobs/?page=${page}&limit=10`);
            setJobs(data.jobs);
            setTotalPages(data.total_pages);
        } catch (err) {
            setError(apiError(err, "Unable to load jobs."));
        } finally {
            setLoading(false);
        }
    }

    async function refreshPending() {
        if (refreshing) return;
        try {
            setRefreshing(true);
            setError("");
            const { data } = await api.post("/jobs/refresh-pending?limit=20");
            setSummary(data);
            await fetchJobs();
        } catch (err) {
            setError(apiError(err, "Unable to refresh pending jobs."));
        } finally {
            setRefreshing(false);
        }
    }

    if (loading && !jobs.length) return <main className="jobs-page"><div className="eyebrow">AUTOLEAD / JOBS</div><h1>Loading <span>jobs...</span></h1></main>;

    return (
        <main className="jobs-page">
            <div className="page-header">
                <div><div className="eyebrow">AUTOLEAD / JOBS</div><h1>Lead generation <span>jobs.</span></h1>
                    <p>Track your lead generation jobs and discovered businesses.</p></div>
                <button className="crystal-button" onClick={refreshPending} disabled={refreshing}>
                    {refreshing ? "Refreshing..." : "Refresh Pending Jobs"}
                </button>
            </div>
            {error && <p className="error-message">{error}</p>}
            {summary && <div className="glass-card refresh-summary">
                Checked {summary.checked}: {summary.completed} completed, {summary.still_processing} processing, {summary.failed} failed, {summary.companies_saved} companies saved.
            </div>}
            <section className="jobs-list">
                {!jobs.length && <div className="glass-card empty-state"><h2>No jobs yet</h2><p>Start your first lead generation job.</p>
                    <Link to="/tools/lead-generation" className="crystal-button">Create Lead Generation Job</Link></div>}
                {jobs.map((job) => (
                    <Link key={job.id} to={`/jobs/${job.id}`} className="job-card glass-card">
                        <div className="job-card-top"><div><div className="job-card-id">JOB #{job.id}</div>
                            <h2>{job.country}{job.province ? ` · ${job.province}` : ""}</h2></div>
                            <span className={`job-status-badge ${job.status}`}>{job.status}</span></div>
                        <div className="job-card-details">
                            <div><span>Industries</span><strong>{job.industries.join(", ")}</strong></div>
                            <div><span>Target Leads</span><strong>{job.lead_count}</strong></div>
                            <div><span>Companies</span><strong>{job.company_count || 0}</strong></div>
                        </div>
                        <div className="job-card-footer"><span>Firecrawl: <strong>{job.firecrawl_status}</strong></span>
                            <span>Overall: <strong>{job.status}</strong></span><span>{new Date(job.created_at).toLocaleString()}</span>
                            <span className="view-job">View Details →</span></div>
                        {job.firecrawl_error && <div className="job-error">{job.firecrawl_error}</div>}
                    </Link>
                ))}
            </section>
            {totalPages > 1 && <div className="pagination">
                <button className="pagination-button" disabled={page === 1} onClick={() => setPage((value) => value - 1)}>← Previous</button>
                <span>Page {page} of {totalPages}</span>
                <button className="pagination-button" disabled={page === totalPages} onClick={() => setPage((value) => value + 1)}>Next →</button>
            </div>}
        </main>
    );
}

export default Jobs;
