import { Link } from "react-router-dom";

function Tools() {
    return (
        <main className="tools-page">

            <div className="eyebrow">
                AUTOLEAD / TOOLS
            </div>

            <div className="tools-header">

                <div>

                    <h1>
                        Lead generation tools.
                    </h1>

                    <p>
                        Create targeted lead generation jobs and discover
                        businesses that match your requirements.
                    </p>

                </div>

            </div>


            <section className="tools-grid">

                <div className="tool-card glass-card">

                    <div className="tool-card-icon">
                        ✦
                    </div>

                    <div className="tool-card-content">

                        <div className="eyebrow">
                            B2B LEAD GENERATION
                        </div>

                        <h2>
                            Business Lead Generator
                        </h2>

                        <p>
                            Discover businesses by country, province,
                            industry, and lead count.
                        </p>

                        <Link
                            to="/tools/lead-generation"
                            className="crystal-button"
                        >
                            Open Tool →
                        </Link>

                    </div>

                </div>


                <div className="tool-card glass-card tool-card-disabled">

                    <div className="tool-card-icon">
                        ◌
                    </div>

                    <div className="tool-card-content">

                        <div className="eyebrow">
                            COMING SOON
                        </div>

                        <h2>
                            AI Data Enrichment
                        </h2>

                        <p>
                            Automatically enrich and improve business
                            information using intelligent data sources.
                        </p>

                        <button
                            className="crystal-button"
                            disabled
                        >
                            Coming Soon
                        </button>

                    </div>

                </div>

            </section>

        </main>
    );
}

export default Tools;