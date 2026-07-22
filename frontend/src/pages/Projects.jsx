import { Link } from "react-router-dom";
import { useEffect, useState } from "react";
import axios from "axios";

function Projects() {
    const [projects, setProjects] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        fetchProjects();
    }, []);

    async function fetchProjects() {
        try {
            const response = await axios.get(
                "http://127.0.0.1:8000/projects"
            );

            setProjects(response.data);

        } catch (error) {
            console.error(error);

            setError(
                "Unable to load projects."
            );

        } finally {
            setLoading(false);
        }
    }


    if (loading) {
        return (
            <main className="projects-page">

                <div className="eyebrow">
                    AUTOLEAD / WORKSPACE
                </div>

                <h1>
                    Loading <span>Projects...</span>
                </h1>

            </main>
        );
    }


    if (error) {
        return (
            <main className="projects-page">

                <div className="eyebrow">
                    AUTOLEAD / WORKSPACE
                </div>

                <h1>
                    Your <span>Projects</span>
                </h1>

                <p className="error-message">
                    {error}
                </p>

            </main>
        );
    }


    return (
        <main className="projects-page">

            {/* Header */}

            <div className="page-header">

                <div>

                    <div className="eyebrow">
                        AUTOLEAD / WORKSPACE
                    </div>

                    <h1>
                        Your <span>Projects</span>
                    </h1>

                    <p>
                        Organize your lead generation jobs and collected business data.
                    </p>

                </div>


                <button className="crystal-button">
                    + New Project
                </button>

            </div>


            {/* Projects */}

            <section className="projects-grid">

                {projects.map((project) => (

                    <Link
                        key={project.id}
                        to={`/projects/${project.id}`}
                        className="project-card glass-card"
                    >

                        <div className="project-card-top">

                            <div className="project-symbol">
                                {project.name
                                    .substring(0, 2)
                                    .toUpperCase()
                                }
                            </div>


                            <span className="status-badge">
                                Active
                            </span>

                        </div>


                        <h2>
                            {project.name}
                        </h2>


                        <p>
                            {project.description ||
                                "No description provided."
                            }
                        </p>


                        <div className="project-meta">

                            <span>
                                Project #{project.id}
                            </span>

                            <span>
                                {new Date(
                                    project.created_at
                                ).toLocaleDateString()}
                            </span>

                        </div>

                    </Link>

                ))}


                {/* Create project card */}

                <div className="project-card glass-card create-project-card">

                    <div className="create-project-icon">
                        +
                    </div>


                    <h2>
                        Create a new project
                    </h2>


                    <p>
                        Start organizing a new lead generation campaign.
                    </p>

                </div>

            </section>

        </main>
    );
}

export default Projects;