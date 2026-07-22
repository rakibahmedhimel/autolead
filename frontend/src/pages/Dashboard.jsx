function Dashboard() {
  return (
    <main className="dashboard-page">
      <header className="dashboard-header">
        <div className="eyebrow">AUTOLEAD / COMMAND CENTER</div>

        <h1>
          Turn data into <span>opportunity.</span>
        </h1>

        <p className="dashboard-description">
          Manage your lead generation tools, projects, jobs, and business data
          from one intelligent workspace.
        </p>
      </header>

      <div className="dashboard-grid">
        <section className="glass-card generation-card">
          <div className="card-heading">
            <div>
              <h2>Lead Generation</h2>
              <p>Generate targeted business leads using AutoLead tools.</p>
            </div>

            <div className="card-icon">✦</div>
          </div>

          <button className="crystal-button">
            Open Tools
          </button>
        </section>

        <section className="glass-card quick-stats-card">
          <h2>Overview</h2>

          <div className="stat-item">
            <span>Total Projects</span>
            <strong>0</strong>
          </div>

          <div className="stat-item">
            <span>Total Jobs</span>
            <strong>0</strong>
          </div>
        </section>
      </div>
    </main>
  );
}

export default Dashboard;