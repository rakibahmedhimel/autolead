export default function LoadingScreen({ compact = false, label = "Loading AutoLead..." }) {
  return (
    <div className={`loading-screen${compact ? " compact" : ""}`} role="status" aria-live="polite">
      <div className="crystal-loader" aria-hidden="true"><span /></div>
      <span>{label}</span>
    </div>
  );
}
