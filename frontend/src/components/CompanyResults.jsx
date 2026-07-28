/* eslint-disable react-refresh/only-export-components */
import { useEffect, useRef, useState } from "react";

export const COMPANY_COLUMNS = [
  ["company_name", "Company Name"], ["industry", "Industry"], ["website", "Website"],
  ["linkedin", "LinkedIn"], ["facebook", "Facebook"], ["instagram", "Instagram"],
  ["owner", "Owner"], ["ceo", "CEO"], ["email", "Email"], ["phone", "Phone"],
  ["headquarters", "Headquarters"], ["company_size", "Company Size"],
  ["contact_page", "Contact Page"], ["services", "Services"],
  ["enrichment_status", "Enrichment Status"],
];
const links = new Set(["website", "linkedin", "facebook", "instagram", "contact_page"]);
const display = (value) => Array.isArray(value) ? value.join(", ") : (value ?? "");

export function downloadCompaniesCsv(rows, filename) {
  const safe = (value) => {
    let text = String(display(value));
    if (/^[=+\-@]/.test(text)) text = `'${text}`;
    return `"${text.replaceAll('"', '""')}"`;
  };
  const csv = [COMPANY_COLUMNS.map(([, label]) => safe(label)).join(","),
    ...rows.map((row) => COMPANY_COLUMNS.map(([key]) => safe(row[key])).join(","))].join("\r\n");
  const blob = new Blob(["\uFEFF", csv], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a"); anchor.href = url; anchor.download = filename; anchor.click();
  URL.revokeObjectURL(url);
}

export default function CompanyResults({ companies, total, page, totalPages, onPageChange, progress, title = "Companies" }) {
  const [view, setView] = useState(() => localStorage.getItem("autolead-company-view") || "sheet");
  const [cell, setCell] = useState(null);
  const sectionRef = useRef(null);
  useEffect(() => { localStorage.setItem("autolead-company-view", view); }, [view]);
  function changePage(next) { onPageChange(next); sectionRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }); }
  const summary = progress && `${progress.completed || 0} enriched · ${progress.pending || 0} pending · ${progress.failed || 0} failed · ${progress.skipped || 0} skipped`;
  return <section className="companies-section" ref={sectionRef}>
    <div className="results-toolbar"><div><div className="eyebrow">RESULTS</div><h2>{title}</h2>
      <p>{total} companies · Page {page} of {Math.max(totalPages, 1)}{summary ? ` · ${summary}` : ""}</p></div>
      <div className="view-switcher" aria-label="Company view">
        <button className={view === "sheet" ? "active" : ""} onClick={() => setView("sheet")}>Sheet View</button>
        <button className={view === "card" ? "active" : ""} onClick={() => setView("card")}>Card View</button>
      </div></div>
    {!companies.length ? <div className="glass-card empty-state"><h3>No companies yet</h3><p>Discovered companies will appear here.</p></div> :
      view === "sheet" ? <div className="company-sheet glass-card"><table><thead><tr><th>#</th>{COMPANY_COLUMNS.map(([, label]) => <th key={label}>{label}</th>)}</tr></thead>
        <tbody>{companies.map((company, index) => <tr key={company.id || index}><td>{(page - 1) * companies.length + index + 1}</td>
          {COMPANY_COLUMNS.map(([key, label]) => { const value = display(company[key]); return <td key={key}>
            <button className="sheet-cell" onClick={() => value && setCell({ label, value, link: links.has(key) })} title={value || "—"}>
              {value ? (links.has(key) ? label : value) : "—"}</button></td>; })}</tr>)}</tbody></table></div>
      : <div className="companies-grid">{companies.map((company) => <div key={company.id} className="company-card glass-card">
        <div className="company-card-header"><div className="company-symbol">{company.company_name?.[0]?.toUpperCase() || "—"}</div>
          <div><h3>{company.company_name || "—"}</h3><span>{company.industry || "—"}</span></div>
          <span className={`enrichment-badge ${company.enrichment_status || ""}`}>{company.enrichment_status || "—"}</span></div>
        <div className="company-details"><p>{company.email || "—"}</p><p>{company.phone || "—"}</p><p>{company.headquarters || "—"}</p></div>
        <div className="company-actions">{[["website","Website"],["linkedin","LinkedIn"],["facebook","Facebook"],["instagram","Instagram"]].map(([key,label]) => company[key] && <a key={key} href={company[key]} target="_blank" rel="noreferrer">{label}</a>)}</div>
      </div>)}</div>}
    {totalPages > 1 && <div className="pagination"><button className="pagination-button" disabled={page === 1} onClick={() => changePage(page - 1)}>← Previous</button>
      <span>Page {page} of {totalPages}</span><button className="pagination-button" disabled={page === totalPages} onClick={() => changePage(page + 1)}>Next →</button></div>}
    {cell && <div className="modal-overlay" onClick={() => setCell(null)}><div className="cell-dialog glass-card" onClick={(e) => e.stopPropagation()}>
      <div className="modal-header"><h3>{cell.label}</h3><button className="modal-close" onClick={() => setCell(null)}>×</button></div><p>{cell.value}</p>
      <div className="modal-actions"><button className="secondary-button" onClick={() => navigator.clipboard.writeText(cell.value)}>Copy</button>
        {cell.link && <a className="crystal-button" href={cell.value} target="_blank" rel="noreferrer">Open Link</a>}</div></div></div>}
  </section>;
}
