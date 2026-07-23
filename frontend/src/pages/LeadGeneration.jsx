import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

function LeadGeneration() {

    const navigate = useNavigate();


    // =========================
    // FORM STATE
    // =========================

    const [country, setCountry] = useState("");

    const [province, setProvince] = useState("");

    const [leadCount, setLeadCount] = useState(10);

    const [industries, setIndustries] = useState([]);


    // =========================
    // PROJECT STATE
    // =========================

    const [projects, setProjects] = useState([]);

    const [selectedProjectId, setSelectedProjectId] = useState("");


    const [showProjectModal, setShowProjectModal] = useState(false);

    const [projectName, setProjectName] = useState("");

    const [projectDescription, setProjectDescription] = useState("");

    const [creatingProject, setCreatingProject] = useState(false);


    // =========================
    // UI STATE
    // =========================

    const [loading, setLoading] = useState(false);

    const [error, setError] = useState("");


    const availableIndustries = [

        "Construction",

        "Retail",

        "Real Estate",

        "Telecom",

        "Automotive & Mobility",

        "Oil & Gas",

        "Salon",

        "Spa"

    ];


    // =========================
    // FETCH PROJECTS
    // =========================

    useEffect(() => {

        fetchProjects();

    }, []);


    async function fetchProjects() {

        try {

            const response = await fetch(
                `${import.meta.env.VITE_API_URL}/projects/`
            );


            if (!response.ok) {

                throw new Error(
                    "Failed to load projects."
                );

            }


            const data = await response.json();


            setProjects(data);


        } catch (error) {

            console.error(error);

            setError(
                "Unable to load projects."
            );

        }

    }


    // =========================
    // TOGGLE INDUSTRY
    // =========================

    const toggleIndustry = (industry) => {

        setIndustries((current) => {

            if (current.includes(industry)) {

                return current.filter(
                    (item) => item !== industry
                );

            }


            return [

                ...current,

                industry

            ];

        });

    };


    // =========================
    // CREATE PROJECT
    // =========================

    async function handleCreateProject(event) {

        event.preventDefault();


        if (!projectName.trim()) {

            return;

        }


        try {

            setCreatingProject(true);


            const response = await fetch(
                `${import.meta.env.VITE_API_URL}/projects/`,
                {

                    method: "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body: JSON.stringify({

                        name:
                            projectName.trim(),

                        description:
                            projectDescription.trim()

                    })

                }

            );


            const data =
                await response.json();


            if (!response.ok) {

                throw new Error(

                    data.detail ||
                    "Failed to create project."

                );

            }


            // Add newly-created project
            // to the existing list

            setProjects((current) => [

                ...current,

                data

            ]);


            // Automatically select
            // the newly-created project

            setSelectedProjectId(
                String(data.id)
            );


            // Clear form

            setProjectName("");

            setProjectDescription("");


            // Close modal

            setShowProjectModal(false);


        } catch (error) {

            setError(
                error.message
            );

        } finally {

            setCreatingProject(false);

        }

    }


    // =========================
    // SUBMIT JOB
    // =========================

    const handleSubmit = async (event) => {

        event.preventDefault();


        setError("");


        if (!selectedProjectId) {

            setError(

                "Please select or create a project."

            );

            return;

        }


        if (!country || !province) {

            setError(

                "Please select a country and province."

            );

            return;

        }


        if (industries.length === 0) {

            setError(

                "Please select at least one industry."

            );

            return;

        }


        try {

            setLoading(true);


            const response = await fetch(

                `${import.meta.env.VITE_API_URL}/jobs/generate`,

                {

                    method: "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body: JSON.stringify({

                        project_id:
                            Number(
                                selectedProjectId
                            ),

                        country:

                            country,

                        province:

                            province,

                        industries:

                            industries,

                        lead_count:

                            Number(
                                leadCount
                            )

                    })

                }

            );


            const data =
                await response.json();


            if (!response.ok) {

                throw new Error(

                    data.detail ||

                    "Failed to start lead generation."

                );

            }


            navigate(
                "/jobs"
            );


        } catch (error) {

            setError(

                error.message

            );

        } finally {

            setLoading(false);

        }

    };


    return (

        <main className="dashboard-page">


            {/* BACK BUTTON */}

            <button

                className="back-button"

                onClick={() =>
                    navigate("/tools")
                }

            >

                ← Back to Tools

            </button>


            {/* HEADER */}

            <header className="dashboard-header">


                <div className="eyebrow">

                    AUTOLEAD / LEAD GENERATION

                </div>


                <h1>

                    Generate targeted

                    <span>
                        leads.
                    </span>

                </h1>


                <p className="dashboard-description">

                    Configure your target market and let AutoLead

                    discover businesses for you.

                </p>


            </header>


            {/* GENERATION CARD */}

            <section className="glass-card generation-card">


                <div className="card-heading">


                    <div>


                        <h2>

                            Create Lead Generation Job

                        </h2>


                        <p>

                            Define where and what kind of businesses

                            you want to discover.

                        </p>


                    </div>


                    <div className="card-icon">

                        ✦

                    </div>


                </div>


                <form onSubmit={handleSubmit}>


                    {/* PROJECT */}

                    <div className="form-group">


                        <label>

                            Project

                        </label>


                        <div className="project-selector-row">


                            <select

                                value={
                                    selectedProjectId
                                }

                                onChange={(event) =>

                                    setSelectedProjectId(

                                        event.target.value

                                    )

                                }

                            >


                                <option value="">

                                    Select a project

                                </option>


                                {projects.map(
                                    (project) => (

                                        <option

                                            key={
                                                project.id
                                            }

                                            value={
                                                project.id
                                            }

                                        >

                                            {
                                                project.name
                                            }

                                        </option>

                                    )

                                )}


                            </select>


                            <button

                                type="button"

                                className="secondary-button"

                                onClick={() =>

                                    setShowProjectModal(
                                        true
                                    )

                                }

                            >

                                + New Project

                            </button>


                        </div>


                    </div>


                    {/* LOCATION + LEAD COUNT */}

                    <div className="form-grid">


                        <div className="form-group">


                            <label>

                                Country

                            </label>


                            <select

                                value={country}

                                onChange={(event) =>

                                    setCountry(

                                        event.target.value

                                    )

                                }

                            >


                                <option value="">

                                    Select country

                                </option>


                                <option value="Canada">

                                    Canada

                                </option>


                                <option value="United States">

                                    United States

                                </option>


                                <option value="Australia">

                                    Australia

                                </option>


                                <option value="United Kingdom">

                                    United Kingdom

                                </option>


                            </select>


                        </div>


                        <div className="form-group">


                            <label>

                                Province / State

                            </label>


                            <input

                                type="text"

                                placeholder="e.g. Alberta"

                                value={province}

                                onChange={(event) =>

                                    setProvince(

                                        event.target.value

                                    )

                                }

                            />


                        </div>


                        <div className="form-group">


                            <label>

                                Number of Leads

                            </label>


                            <input

                                type="number"

                                min="1"

                                max="100"

                                value={leadCount}

                                onChange={(event) =>

                                    setLeadCount(

                                        event.target.value

                                    )

                                }

                            />


                        </div>


                    </div>


                    {/* INDUSTRIES */}

                    <div className="form-group industries-group">


                        <label>

                            Target Industries

                        </label>


                        <div className="industry-tags">


                            {availableIndustries.map(

                                (industry) => (


                                    <button

                                        type="button"

                                        key={industry}

                                        className={

                                            industries.includes(

                                                industry

                                            )

                                                ? "industry-tag active"

                                                : "industry-tag"

                                        }

                                        onClick={() =>

                                            toggleIndustry(

                                                industry

                                            )

                                        }

                                    >

                                        {industry}

                                    </button>


                                )

                            )}


                        </div>


                    </div>


                    {/* ERROR */}

                    {error && (


                        <p

                            style={{

                                color: "#ff7b8a",

                                marginTop: "20px"

                            }}

                        >

                            {error}

                        </p>


                    )}


                    {/* SUBMIT */}

                    <button

                        type="submit"

                        className="crystal-button"

                        disabled={loading}

                    >


                        {loading

                            ? "Starting Job..."

                            : "Start Lead Generation"

                        }


                    </button>


                </form>


            </section>


            {/* CREATE PROJECT MODAL */}

            {showProjectModal && (


                <div

                    className="modal-overlay"

                    onClick={() =>

                        setShowProjectModal(false)

                    }

                >


                    <div

                        className="project-modal glass-card"

                        onClick={(event) =>

                            event.stopPropagation()

                        }

                    >


                        <div className="modal-header">


                            <div>


                                <div className="eyebrow">

                                    AUTOLEAD / PROJECT

                                </div>


                                <h2>

                                    Create New Project

                                </h2>


                            </div>


                            <button

                                className="modal-close"

                                onClick={() =>

                                    setShowProjectModal(false)

                                }

                            >

                                ×

                            </button>


                        </div>


                        <form

                            onSubmit={
                                handleCreateProject
                            }

                        >


                            <div className="form-group">


                                <label>

                                    Project Name

                                </label>


                                <input

                                    type="text"

                                    placeholder="e.g. Alberta Telecom Leads"

                                    value={
                                        projectName
                                    }

                                    onChange={(event) =>

                                        setProjectName(

                                            event.target.value

                                        )

                                    }

                                />

                            </div>


                            <div className="form-group">


                                <label>

                                    Description

                                </label>


                                <textarea

                                    placeholder="Describe this project..."

                                    value={
                                        projectDescription
                                    }

                                    onChange={(event) =>

                                        setProjectDescription(

                                            event.target.value

                                        )

                                    }

                                />

                            </div>


                            <div className="modal-actions">


                                <button

                                    type="button"

                                    className="secondary-button"

                                    onClick={() =>

                                        setShowProjectModal(false)

                                    }

                                >

                                    Cancel

                                </button>


                                <button

                                    type="submit"

                                    className="crystal-button"

                                    disabled={

                                        creatingProject

                                    }

                                >

                                    {creatingProject

                                        ? "Creating..."

                                        : "Create Project"

                                    }

                                </button>


                            </div>


                        </form>


                    </div>


                </div>

            )}


        </main>

    );

}


export default LeadGeneration;