import { Link, useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import axios from "axios";


function ProjectDetails() {


    const { projectId } = useParams();


    const [project, setProject] = useState(null);

    const [jobs, setJobs] = useState([]);

    const [companies, setCompanies] = useState([]);


    const [jobsPage, setJobsPage] = useState(1);

    const [companiesPage, setCompaniesPage] = useState(1);


    const [jobsTotalPages, setJobsTotalPages] =
        useState(0);

    const [companiesTotalPages, setCompaniesTotalPages] =
        useState(0);


    const [loading, setLoading] =
        useState(true);

    const [error, setError] =
        useState("");


    useEffect(() => {

        fetchProject();

    }, [projectId]);


    useEffect(() => {

        fetchJobs();

    }, [
        projectId,
        jobsPage
    ]);


    useEffect(() => {

        fetchCompanies();

    }, [
        projectId,
        companiesPage
    ]);


    async function fetchProject() {

        try {

            const response = await axios.get(

                `http://127.0.0.1:8000/projects/${projectId}`

            );


            setProject(
                response.data
            );


        } catch (error) {

            console.error(error);

            setError(
                "Unable to load project."
            );

        } finally {

            setLoading(false);

        }

    }


    async function fetchJobs() {

        try {

            const response = await axios.get(

                `http://127.0.0.1:8000/projects/${projectId}/jobs?page=${jobsPage}&limit=10`

            );


            setJobs(
                response.data.jobs
            );


            setJobsTotalPages(
                response.data.total_pages
            );


        } catch (error) {

            console.error(
                "Unable to load jobs.",
                error
            );

        }

    }


    async function fetchCompanies() {

        try {

            const response = await axios.get(

                `http://127.0.0.1:8000/projects/${projectId}/companies?page=${companiesPage}&limit=10`

            );


            setCompanies(
                response.data.companies
            );


            setCompaniesTotalPages(
                response.data.total_pages
            );


        } catch (error) {

            console.error(
                "Unable to load companies.",
                error
            );

        }

    }


    function getStatusClass(status) {

        if (!status) {

            return "";

        }


        return status.toLowerCase();

    }


    if (loading) {

        return (

            <main className="project-details-page">

                <div className="eyebrow">

                    AUTOLEAD / PROJECT

                </div>


                <h1>

                    Loading <span>Project...</span>

                </h1>

            </main>

        );

    }


    if (error || !project) {

        return (

            <main className="project-details-page">

                <div className="eyebrow">

                    AUTOLEAD / PROJECT

                </div>


                <h1>

                    Project not found

                </h1>


                <p>

                    {error}

                </p>


                <Link
                    to="/projects"
                    className="back-link"
                >

                    ← Back to Projects

                </Link>

            </main>

        );

    }


    return (

        <main className="project-details-page">


            {/* BACK */}

            <Link

                to="/projects"

                className="back-link"

            >

                ← Back to Projects

            </Link>


            {/* HEADER */}

            <div className="project-details-header">


                <div>


                    <div className="eyebrow">

                        AUTOLEAD / PROJECT

                    </div>


                    <h1>

                        {project.name}

                    </h1>


                    <p>

                        {project.description ||

                            "No description provided."

                        }

                    </p>


                </div>


                <Link

                    to="/tools/lead-generation"

                    className="crystal-button"

                >

                    + New Lead Job

                </Link>


            </div>


            {/* PROJECT STATS */}

            <section className="project-stats">


                <div className="glass-card project-stat-card">


                    <span>

                        Project ID

                    </span>


                    <strong>

                        #{project.id}

                    </strong>


                </div>


                <div className="glass-card project-stat-card">


                    <span>

                        Created

                    </span>


                    <strong>

                        {new Date(

                            project.created_at

                        ).toLocaleDateString()}

                    </strong>


                </div>


                <div className="glass-card project-stat-card">


                    <span>

                        Jobs

                    </span>


                    <strong>

                        {jobs.length}

                    </strong>


                </div>


                <div className="glass-card project-stat-card">


                    <span>

                        Companies

                    </span>


                    <strong>

                        {companies.length}

                    </strong>


                </div>


            </section>


            {/* JOBS */}

            <section className="project-section">


                <div className="section-header">


                    <div>


                        <div className="eyebrow">

                            PROJECT ACTIVITY

                        </div>


                        <h2>

                            Lead Generation Jobs

                        </h2>


                        <p>

                            Jobs created inside this project.

                        </p>


                    </div>


                    <Link

                        to="/tools/lead-generation"

                        className="crystal-button"

                    >

                        + New Job

                    </Link>


                </div>


                <div className="project-jobs-list">


                    {jobs.length === 0 && (

                        <div className="glass-card empty-state">

                            <h3>

                                No jobs yet

                            </h3>


                            <p>

                                Start a lead generation job

                                for this project.

                            </p>

                        </div>

                    )}


                    {jobs.map((job) => {


                        const status =

                            job.firecrawl_status ||

                            job.status;


                        return (

                            <Link

                                key={job.id}

                                to={`/jobs/${job.id}`}

                                className="project-job-row glass-card"

                            >


                                <div>


                                    <span className="job-card-id">

                                        JOB #{job.id}

                                    </span>


                                    <h3>

                                        {job.country}

                                        {job.province &&

                                            ` · ${job.province}`

                                        }

                                    </h3>


                                </div>


                                <div className="project-job-meta">


                                    <span>

                                        {job.industries.join(

                                            ", "

                                        )}

                                    </span>


                                    <span>

                                        {job.lead_count}

                                        {" "}target leads

                                    </span>


                                </div>


                                <span

                                    className={

                                        `job-status-badge ${getStatusClass(

                                            status

                                        )}`

                                    }

                                >

                                    {status}

                                </span>


                            </Link>

                        );

                    })}


                </div>


                {jobsTotalPages > 1 && (

                    <div className="pagination">


                        <button

                            className="pagination-button"

                            disabled={jobsPage === 1}

                            onClick={() =>

                                setJobsPage(

                                    jobsPage - 1

                                )

                            }

                        >

                            ← Previous

                        </button>


                        <span>

                            Page {jobsPage}

                            {" "}of{" "}

                            {jobsTotalPages}

                        </span>


                        <button

                            className="pagination-button"

                            disabled={

                                jobsPage ===

                                jobsTotalPages

                            }

                            onClick={() =>

                                setJobsPage(

                                    jobsPage + 1

                                )

                            }

                        >

                            Next →

                        </button>


                    </div>

                )}

            </section>


            {/* COMPANIES */}

            <section className="project-section">


                <div className="section-header">


                    <div>


                        <div className="eyebrow">

                            PROJECT LEADS

                        </div>


                        <h2>

                            Collected Companies

                        </h2>


                        <p>

                            Businesses discovered across all jobs

                            in this project.

                        </p>


                    </div>


                </div>


                <div className="companies-grid">


                    {companies.length === 0 && (

                        <div className="glass-card empty-state">

                            <h3>

                                No companies yet

                            </h3>


                            <p>

                                Companies discovered by jobs

                                will appear here.

                            </p>

                        </div>

                    )}


                    {companies.map((company) => (

                        <div

                            key={company.id}

                            className="company-card glass-card"

                        >


                            <div className="company-card-header">


                                <div className="company-symbol">

                                    {company.company_name

                                        ?.charAt(0)

                                        .toUpperCase()

                                    }

                                </div>


                                <div>

                                    <h3>

                                        {company.company_name}

                                    </h3>


                                    <span>

                                        {company.industry}

                                    </span>

                                </div>


                            </div>


                            <div className="company-details">


                                {company.email && (

                                    <p>

                                        ✉ {company.email}

                                    </p>

                                )}


                                {company.phone && (

                                    <p>

                                        ☎ {company.phone}

                                    </p>

                                )}


                                {company.headquarters && (

                                    <p>

                                        📍 {company.headquarters}

                                    </p>

                                )}

                            </div>


                            <div className="company-actions">


                                {company.website && (

                                    <a

                                        href={company.website}

                                        target="_blank"

                                        rel="noreferrer"

                                        className="company-action-button"

                                    >

                                        Website

                                    </a>

                                )}


                                {company.linkedin && (

                                    <a

                                        href={company.linkedin}

                                        target="_blank"

                                        rel="noreferrer"

                                        className="company-action-button"

                                    >

                                        LinkedIn

                                    </a>

                                )}

                            </div>


                        </div>

                    ))}


                </div>


                {companiesTotalPages > 1 && (

                    <div className="pagination">


                        <button

                            className="pagination-button"

                            disabled={

                                companiesPage === 1

                            }

                            onClick={() =>

                                setCompaniesPage(

                                    companiesPage - 1

                                )

                            }

                        >

                            ← Previous

                        </button>


                        <span>

                            Page {companiesPage}

                            {" "}of{" "}

                            {companiesTotalPages}

                        </span>


                        <button

                            className="pagination-button"

                            disabled={

                                companiesPage ===

                                companiesTotalPages

                            }

                            onClick={() =>

                                setCompaniesPage(

                                    companiesPage + 1

                                )

                            }

                        >

                            Next →

                        </button>


                    </div>

                )}


            </section>


        </main>

    );

}


export default ProjectDetails;