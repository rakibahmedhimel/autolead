import { useEffect, useState } from "react";
import api, { apiError } from "../api/client";
import LoadingScreen from "../components/LoadingScreen";
export default function AdminDashboard() {
  const [data, setData] = useState(null),
    [contacts, setContacts] = useState([]),
    [requests, setRequests] = useState([]),
    [error, setError] = useState("");
  useEffect(() => {
    Promise.all([
      api.get("/admin/dashboard"),
      api.get("/admin/contact-submissions"),
      api.get("/admin/tool-requests"),
    ])
      .then(([d, c, r]) => {
        setData(d.data);
        setContacts(c.data);
        setRequests(r.data);
      })
      .catch((e) => setError(apiError(e)));
  }, []);
  if (!data)
    return (
      <main className="dashboard-page">
        {error ? <h1>{error}</h1> : <LoadingScreen />}
      </main>
    );
  return (
    <main className="dashboard-page">
      <div className="eyebrow">AUTOLEAD / ADMIN</div>
      <h1>
        System <span>overview.</span>
      </h1>
      <section className="project-stats">
        {[
          ["Users", data.total_users],
          ["Projects", data.total_projects],
          ["Jobs", data.total_jobs],
          ["Companies", data.total_companies],
          ["Spreadsheet Rows", data.total_spreadsheet_rows],
          ["Credits", data.credits_used],
        ].map((x) => (
          <div className="glass-card project-stat-card" key={x[0]}>
            <span>{x[0]}</span>
            <strong>{x[1]}</strong>
          </div>
        ))}
      </section>
      <section className="glass-card generation-card">
        <h2>User usage</h2>
        <div className="admin-table">
          {data.users.map((u) => (
            <div className="project-job-row" key={u.id}>
              <div>
                <strong>{u.name}</strong>
                <p>{u.email}</p>
              </div>
              <span>
                {u.projects} projects · {u.jobs} jobs · {u.companies} leads
              </span>
              <span>{u.credits_used} credits</span>
            </div>
          ))}
        </div>
      </section>
      <section className="glass-card generation-card">
        <h2>Contact submissions</h2>
        {contacts.map((c) => (
          <div className="project-job-row" key={c.id}>
            <strong>{c.subject}</strong>
            <span>
              {c.name} · {c.email}
            </span>
            <p>{c.message}</p>
          </div>
        ))}
      </section>
      <section className="glass-card generation-card">
        <h2>Tool requests</h2>
        {requests.map((r) => (
          <div className="project-job-row" key={r.id}>
            <strong>{r.tool_name}</strong>
            <span>{r.status}</span>
            <p>{r.business_problem}</p>
          </div>
        ))}
      </section>
    </main>
  );
}
