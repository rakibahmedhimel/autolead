import { Link, useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import axios from "axios";

function JobDetails() {

    const { jobId } = useParams();

    const [job, setJob] = useState(null);

    const [loading, setLoading] = useState(true);

    const [error, setError] = useState("");


    useEffect(() => {

        fetchJob();

    }, [jobId]);


    async function fetchJob() {

        try {

            const response = await axios.get(
                `http://127.0.0.1:8000/jobs/${jobId}`
            );

            setJob(response.data);

        } catch (error) {

            console.error(error);

            setError(
                "Unable to load job details."
            );

        } finally {

            setLoading(false);

        }

    }


    if (loading) {

        return (

            <main className="job-details-page">

                <div className="eyebrow">
                    AUTOLEAD / JOB
                </div>

                <h1>
                    Loading job...
                </h1>

            </main>

        );

    }


    if (error || !job) {

        return (

            <main className="job-details-page">

                <div className="eyebrow">
                    AUTOLEAD / JOB
                </div>

                <h1>
                    Job not found
                </h1>

                <p>
                    {error}
                </p>

                <Link
                    to="/jobs"
                    className="back-link"
                >
                    ← Back to Jobs
                </Link>

            </main>

        );

    }


    return (

        <main className="job-details-page">


            {/* Back */}

            <Link
                to="/jobs"
                className="back-link"
            >
                ← Back to Jobs
            </Link>


            {/* Header */}

            <div className="job-details-header">


                <div>

                    <div className="eyebrow">
                        AUTOLEAD / JOB
                    </div>


                    <h1>
                        Job #{job.id}
                    </h1>


                    <p>

                        {job.country}

                        {job.province &&
                            ` · ${job.province}`
                        }

                    </p>

                </div>


                <div
                    className={`job-status-badge ${job.status}`}
                >

                    {job.status}

                </div>


            </div>


            {/* Job Information */}

            <section className="job-info-grid">


                <div className="glass-card job-info-card">

                    <span>
                        Industries
                    </span>


                    <strong>

                        {job.industries.join(", ")}

                    </strong>

                </div>


                <div className="glass-card job-info-card">

                    <span>
                        Target Leads
                    </span>


                    <strong>
                        {job.lead_count}
                    </strong>

                </div>


                <div className="glass-card job-info-card">

                    <span>
                        Companies Found
                    </span>


                    <strong>
                        {job.companies.length}
                    </strong>

                </div>


            </section>


            {/* Companies */}

            <section className="companies-section">


                <div className="section-header">


                    <div>

                        <div className="eyebrow">
                            RESULTS
                        </div>


                        <h2>
                            Companies
                        </h2>


                        <p>
                            Businesses discovered by this lead generation job.
                        </p>

                    </div>


                    <button className="crystal-button">

                        ↓ Download

                    </button>

                </div>


                <div className="companies-grid">


                    {job.companies.map((company) => (

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


            </section>


        </main>

    );

}


export default JobDetails;