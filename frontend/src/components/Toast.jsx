import { useEffect } from "react";

export default function Toast({ toast, onClose }) {
  useEffect(() => {
    if (!toast) return undefined;
    const timer = setTimeout(onClose, 4500);
    return () => clearTimeout(timer);
  }, [toast, onClose]);
  if (!toast) return null;
  return <div className={`app-toast ${toast.type || "success"}`} role="status">
    <div><strong>{toast.title}</strong>{toast.body && <p>{toast.body}</p>}</div>
    <button onClick={onClose} aria-label="Dismiss notification">×</button>
  </div>;
}
