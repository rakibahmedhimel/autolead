import { useEffect, useRef, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import api, { apiError } from "../api/client";

const availableIndustries = [
    "Construction", "Retail", "Real Estate", "Telecom",
    "Automotive & Mobility", "Oil & Gas", "Salon", "Spa",
];

function LeadGeneration() {
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const [projects, setProjects] = useState([]);
    const [selectedProjectId, setSelectedProjectId] = useState(searchParams.get("projectId") || "");
    const [country, setCountry] = useState("");
    const [province, setProvince] = useState("");
    const [leadCount, setLeadCount] = useState(10);
    const [industries, setIndustries] = useState([]);
    const [showProjectModal, setShowProjectModal] = useState(false);
    const [projectName, setProjectName] = useState("");
    const [projectDescription, setProjectDescription] = useState("");
    const [creatingProject, setCreatingProject] = useState(false);
    const [activeJob, setActiveJob] = useState(null);
    const [enrichment, setEnrichment] = useState(null);
    const [loading, setLoading] = useState(false);
    const [refreshing, setRefreshing] = useState(false);
    const [enriching, setEnriching] = useState(false);
    const [error, setError] = useState("");
    const projectSubmitGuard = useRef(false);
    const jobSubmitGuard = useRef(false);
    const jobIdempotencyKey = useRef(null);

    useEffect(() => {
        api.get("/projects/").then(({ data }) => setProjects(data))
            .catch((err) => setError(apiError(err, "Unable to load projects.")));
    }, []);

    const selectedProject = projects.find((project) => String(project.id) === String(selectedProjectId));

    function toggleIndustry(industry) {
        setIndustries((current) => current.includes(industry)
            ? current.filter((item) => item !== industry)
            : [...current, industry]);
    }

    async function handleCreateProject(event) {
        event.preventDefault();
        if (!projectName.trim() || projectSubmitGuard.current) return;
        projectSubmitGuard.current = true;
        try {
            setCreatingProject(true);
            setError("");
            const { data } = await api.post("/projects/", {
                name: projectName.trim(), description: projectDescription.trim() || null,
            });
            setProjects((current) => [...current, data]);
            setSelectedProjectId(String(data.id));
            setShowProjectModal(false);
            setProjectName("");
            setProjectDescription("");
        } catch (err) {
            const existingId = err.response?.data?.detail?.existing_project_id;
            if (existingId) setSelectedProjectId(String(existingId));
            setError(apiError(err, "Failed to create project."));
        } finally {
            setCreatingProject(false);
            projectSubmitGuard.current = false;
        }
    }

    async function handleSubmit(event) {
        event.preventDefault();
        if (jobSubmitGuard.current) return;
        if (!selectedProjectId) return setError("Please select or create a project.");
        if (!country) return setError("Please select a country.");
        if (!industries.length) return setError("Please select at least one industry.");
        try {
            jobSubmitGuard.current = true;
            setLoading(true);
            setError("");
            jobIdempotencyKey.current ||= crypto.randomUUID();
            const { data } = await api.post("/jobs/generate", {
                project_id: Number(selectedProjectId), country,
                province: province.trim() || null, industries,
                lead_count: Number(leadCount),
            }, { headers: { "Idempotency-Key": jobIdempotencyKey.current } });
            setActiveJob({ ...data, project_name: selectedProject?.name, companies_saved: 0 });
            jobIdempotencyKey.current = null;
        } catch (err) {
            setError(apiError(err, "Failed to start lead generation."));
        } finally {
            setLoading(false);
            jobSubmitGuard.current = false;
        }
    }

    async function refreshJob() {
        if (!activeJob || refreshing) return;
        try {
            setRefreshing(true);
            setError("");
            const { data } = await api.post(`/jobs/${activeJob.job_id}/refresh`);
            setActiveJob((current) => ({ ...current, ...data }));
        } catch (err) {
            setError(apiError(err, "Unable to refresh this job."));
        } finally {
            setRefreshing(false);
        }
    }

    async function enrichJob() {
        if (!activeJob || enriching) return;
        try {
            setEnriching(true);
            setError("");
            const { data } = await api.post(`/jobs/${activeJob.job_id}/enrich?limit=5`);
            setEnrichment(data);
        } catch (err) {
            setError(apiError(err, "Unable to enrich companies."));
        } finally {
            setEnriching(false);
        }
    }

    return (
        <main className="dashboard-page">
            <button className="back-button" onClick={() => navigate("/tools")}>← Back to Tools</button>
            <header className="dashboard-header">
                <div className="eyebrow">AUTOLEAD / LEAD GENERATION</div>
                <h1>Generate targeted <span>leads.</span></h1>
                <p className="dashboard-description">Configure your target market and let AutoLead discover businesses for you.</p>
            </header>

            <section className="glass-card generation-card">
                <div className="card-heading">
                    <div><h2>Create Lead Generation Job</h2><p>Define where and what kind of businesses you want to discover.</p></div>
                    <div className="card-icon">✦</div>
                </div>
                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label>Project</label>
                        <div className="project-selector-row">
                            <select value={selectedProjectId} onChange={(e) => setSelectedProjectId(e.target.value)}>
                                <option value="">Select a project</option>
                                {projects.map((project) => <option key={project.id} value={project.id}>{project.name}</option>)}
                            </select>
                            <button type="button" className="secondary-button" onClick={() => setShowProjectModal(true)}>+ New Project</button>
                        </div>
                    </div>
                    <div className="form-grid">
                        <div className="form-group"><label>Country</label>
                            <select value={country} onChange={(e) => setCountry(e.target.value)}>
                                <option value="">Select country</option>
                                <option value="Canada">Canada</option><option value="United States">United States</option>
                                <option value="Australia">Australia</option><option value="United Kingdom">United Kingdom</option>
                            </select>
                        </div>
                        <div className="form-group"><label>Province / State (optional)</label>
                            <input placeholder="e.g. Alberta" value={province} onChange={(e) => setProvince(e.target.value)} />
                        </div>
                        <div className="form-group"><label>Number of Leads</label>
                            <input type="number" min="1" max="100" value={leadCount} onChange={(e) => setLeadCount(e.target.value)} />
                        </div>
                    </div>
                    <div className="form-group industries-group"><label>Target Industries</label>
                        <div className="industry-tags">{availableIndustries.map((industry) => (
                            <button type="button" key={industry} className={`industry-tag ${industries.includes(industry) ? "active" : ""}`}
                                onClick={() => toggleIndustry(industry)}>{industry}</button>
                        ))}</div>
                    </div>
                    {error && <p className="error-message">{error}</p>}
                    <button type="submit" className="crystal-button" disabled={loading}>{loading ? "Starting Job..." : "Start Lead Generation"}</button>
                </form>
            </section>

            {activeJob && <section className={`glass-card active-job-panel ${activeJob.status}`}>
                <div>
                    <div className="eyebrow">ACTIVE JOB / #{activeJob.job_id}</div>
                    <h2>{activeJob.status === "completed" ? "Companies are ready" : activeJob.status === "failed" ? "Job failed" : "Firecrawl is processing"}</h2>
                    <p>Project: {activeJob.project_name || selectedProject?.name} · Status: {activeJob.firecrawl_status}</p>
                    {activeJob.companies_saved > 0 && <p>{activeJob.companies_saved} new companies saved ({activeJob.total_companies} total).</p>}
                    {activeJob.error && <p className="error-message">{activeJob.error}</p>}
                    {enrichment && <p>Enrichment: {enrichment.completed} completed, {enrichment.failed} failed, {enrichment.skipped} skipped, {enrichment.remaining} remaining.</p>}
                </div>
                <div className="active-job-actions">
                    {activeJob.status !== "completed" && <button className="crystal-button" onClick={refreshJob} disabled={refreshing}>{refreshing ? "Refreshing..." : "Refresh Status"}</button>}
                    {activeJob.status === "completed" && <button className="crystal-button" onClick={enrichJob} disabled={enriching}>{enriching ? "Enriching..." : "Enrich Missing Social Links"}</button>}
                    <Link className="secondary-button" to="/jobs">View Jobs</Link>
                    <Link className="secondary-button" to={`/jobs/${activeJob.job_id}`}>View Job Details</Link>
                </div>
            </section>}

            {showProjectModal && <div className="modal-overlay" onClick={() => setShowProjectModal(false)}>
                <div className="project-modal glass-card" onClick={(e) => e.stopPropagation()}>
                    <div className="modal-header"><div><div className="eyebrow">AUTOLEAD / PROJECT</div><h2>Create New Project</h2></div>
                        <button type="button" className="modal-close" onClick={() => setShowProjectModal(false)}>×</button></div>
                    <form onSubmit={handleCreateProject}>
                        <div className="form-group"><label>Project Name</label><input value={projectName} onChange={(e) => setProjectName(e.target.value)} /></div>
                        <div className="form-group"><label>Description</label><textarea value={projectDescription} onChange={(e) => setProjectDescription(e.target.value)} /></div>
                        <div className="modal-actions"><button type="button" className="secondary-button" onClick={() => setShowProjectModal(false)}>Cancel</button>
                            <button className="crystal-button" disabled={creatingProject}>{creatingProject ? "Creating..." : "Create Project"}</button></div>
                    </form>
                </div>
            </div>}
        </main>
    );
}

export default LeadGeneration;
