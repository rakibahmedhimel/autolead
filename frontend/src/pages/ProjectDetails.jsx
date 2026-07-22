import { Link, useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import axios from "axios";

function ProjectDetails() {
    const { projectId } = useParams();

    const [project, setProject] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        fetchProject();
    }, [projectId]);

    async function fetchProject() {
        try {
            const response = await axios.get(
                `http://127.0.0.1:8000/projects/${projectId}`
            );

            setProject(response.data);

        } catch (error) {
            console.error(error);
            setError("Unable to load project.");

        } finally {
            setLoading(false);
        }
    }

    if (loading) {
        return (
            <main className="project-details-page">

                <div className="eyebrow">
                    AUTOLEAD / PROJECT
                </div>

                <h1>
                    Loading project...
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
                    className="text-button"
                >
                    ← Back to Projects
                </Link>

            </main>
        );
    }

    return (
        <main className="project-details-page">

            {/* Back */}

            <Link
                to="/projects"
                className="back-link"
            >
                ← Back to Projects
            </Link>


            {/* Project Header */}

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


                <button className="crystal-button">
                    + New Job
                </button>

            </div>


            {/* Jobs Section */}

            <section className="jobs-section">

                <div className="section-header">

                    <div>

                        <h2>
                            Jobs
                        </h2>

                        <p>
                            Lead generation jobs created inside this project.
                        </p>

                    </div>

                </div>


                <div className="jobs-list">

                    {project.jobs && project.jobs.length > 0 ? (

                        project.jobs.map((job) => (

                            <Link
                                key={job.id}
                                to={`/jobs/${job.id}`}
                                className="job-card glass-card"
                            >

                                <div className="job-card-main">

                                    <div className="job-icon">
                                        #
                                    </div>


                                    <div>

                                        <h3>
                                            Job #{job.id}
                                        </h3>


                                        <p>

                                            {job.country}

                                            {job.province &&
                                                ` · ${job.province}`
                                            }

                                        </p>

                                    </div>

                                </div>


                                <div className="job-card-details">


                                    <div>

                                        <span>
                                            Industries
                                        </span>


                                        <strong>

                                            {job.industries &&
                                                job.industries.join(", ")
                                            }

                                        </strong>

                                    </div>


                                    <div>

                                        <span>
                                            Status
                                        </span>


                                        <strong
                                            className={`job-status ${job.status}`}
                                        >
                                            {job.status}
                                        </strong>

                                    </div>


                                    <div>

                                        <span>
                                            Companies
                                        </span>


                                        <strong>

                                            {job.companies
                                                ? job.companies.length
                                                : 0
                                            }

                                        </strong>

                                    </div>


                                </div>

                            </Link>

                        ))

                    ) : (

                        <div className="empty-state glass-card">

                            <h3>
                                No jobs yet
                            </h3>

                            <p>
                                Create your first lead generation job for this project.
                            </p>

                            <button className="crystal-button">
                                Create First Job
                            </button>

                        </div>

                    )}

                </div>

            </section>

        </main>
    );
}

export default ProjectDetails;