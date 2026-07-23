import { Link } from "react-router-dom";
import { useEffect, useState } from "react";
import axios from "axios";

function Jobs() {

    const [jobs, setJobs] = useState([]);

    const [page, setPage] = useState(1);

    const [totalPages, setTotalPages] = useState(0);

    const [loading, setLoading] = useState(true);

    const [error, setError] = useState("");


    useEffect(() => {

        fetchJobs();

    }, [page]);


    async function fetchJobs() {

        try {

            setLoading(true);

            const response = await axios.get(
                `http://127.0.0.1:8000/jobs/?page=${page}&limit=10`
            );

            setJobs(
                response.data.jobs
            );

            setTotalPages(
                response.data.total_pages
            );

        } catch (error) {

            console.error(error);

            setError(
                "Unable to load jobs."
            );

        } finally {

            setLoading(false);

        }

    }


    function getStatusClass(status) {

        if (!status) {
            return "";
        }

        return status.toLowerCase();

    }


    function getJobStatus(job) {

        if (
            job.firecrawl_status === "failed"
        ) {

            return {
                label: "Failed",
                className: "failed"
            };

        }


        if (
            job.firecrawl_status === "processing"
        ) {

            return {
                label: "Processing",
                className: "processing"
            };

        }


        if (
            job.firecrawl_status === "completed"
        ) {

            return {
                label: "Completed",
                className: "completed"
            };

        }


        return {
            label: job.status,
            className: getStatusClass(
                job.status
            )
        };

    }


    if (loading) {

        return (

            <main className="jobs-page">

                <div className="eyebrow">
                    AUTOLEAD / JOBS
                </div>

                <h1>
                    Loading <span>Jobs...</span>
                </h1>

            </main>

        );

    }


    if (error) {

        return (

            <main className="jobs-page">

                <div className="eyebrow">
                    AUTOLEAD / JOBS
                </div>

                <h1>
                    Your <span>Jobs</span>
                </h1>

                <p className="error-message">
                    {error}
                </p>

            </main>

        );

    }


    return (

        <main className="jobs-page">


            {/* Header */}

            <div className="page-header">

                <div>

                    <div className="eyebrow">
                        AUTOLEAD / JOBS
                    </div>


                    <h1>
                        Lead generation <span>jobs.</span>
                    </h1>


                    <p>
                        Track your lead generation jobs and discovered businesses.
                    </p>

                </div>

            </div>


            {/* Jobs */}

            <section className="jobs-list">


                {jobs.length === 0 && (

                    <div className="glass-card empty-state">

                        <h2>
                            No jobs yet
                        </h2>

                        <p>
                            Start your first lead generation job to discover businesses.
                        </p>

                        <Link
                            to="/tools/lead-generation"
                            className="crystal-button"
                        >
                            Create Lead Generation Job
                        </Link>

                    </div>

                )}


                {jobs.map((job) => {

                    const status =
                        getJobStatus(job);


                    return (

                        <Link
                            key={job.id}
                            to={`/jobs/${job.id}`}
                            className="job-card glass-card"
                        >


                            <div className="job-card-top">


                                <div>

                                    <div className="job-card-id">
                                        JOB #{job.id}
                                    </div>


                                    <h2>

                                        {job.country}

                                        {job.province &&
                                            ` · ${job.province}`
                                        }

                                    </h2>

                                </div>


                                <span
                                    className={
                                        `job-status-badge ${status.className}`
                                    }
                                >

                                    {status.className === "processing" &&
                                        "⟳ "
                                    }

                                    {status.className === "completed" &&
                                        "✓ "
                                    }

                                    {status.className === "failed" &&
                                        "✕ "
                                    }

                                    {status.label}

                                </span>

                            </div>


                            <div className="job-card-details">


                                <div>

                                    <span>
                                        Industries
                                    </span>

                                    <strong>
                                        {job.industries.join(", ")}
                                    </strong>

                                </div>


                                <div>

                                    <span>
                                        Target Leads
                                    </span>

                                    <strong>
                                        {job.lead_count}
                                    </strong>

                                </div>


                                <div>

                                    <span>
                                        Companies
                                    </span>

                                    <strong>
                                        {job.companies?.length || 0}
                                    </strong>

                                </div>


                            </div>


                            <div className="job-card-footer">


                                <span>

                                    Firecrawl:{" "}

                                    <strong>
                                        {job.firecrawl_status}
                                    </strong>

                                </span>


                                <span>

                                    {new Date(
                                        job.created_at
                                    ).toLocaleString()}

                                </span>


                                <span className="view-job">
                                    View Details →
                                </span>

                            </div>


                            {job.firecrawl_status === "failed" &&
                                job.firecrawl_error && (

                                    <div className="job-error">

                                        ✕ {job.firecrawl_error}

                                    </div>

                                )
                            }


                        </Link>

                    );

                })}


            </section>


            {/* Pagination */}

            {totalPages > 1 && (

                <div className="pagination">


                    <button
                        className="pagination-button"
                        disabled={page === 1}
                        onClick={() =>
                            setPage(
                                page - 1
                            )
                        }
                    >

                        ← Previous

                    </button>


                    <span>

                        Page {page} of {totalPages}

                    </span>


                    <button
                        className="pagination-button"
                        disabled={
                            page === totalPages
                        }
                        onClick={() =>
                            setPage(
                                page + 1
                            )
                        }
                    >

                        Next →

                    </button>


                </div>

            )}

        </main>

    );

}


export default Jobs;