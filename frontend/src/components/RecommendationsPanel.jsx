import { useEffect, useState } from "react";

function priorityColor(p) {
  if (p === "HIGH") return "#dc2626";
  if (p === "MEDIUM") return "#d97706";
  return "#16a34a";
}

function RecommendationsPanel({ mineId }) {
  const [recs, setRecs] = useState([]);

  useEffect(() => {
    fetch(`http://localhost:8000/api/recommendations?mine_id=${mineId}`)
      .then(r => r.json())
      .then(setRecs);
  }, [mineId]);

  if (recs.length === 0) return <p>Loading recommendations...</p>;

  return (
    <div style={{ border: "1px solid #ddd", borderRadius: 8, padding: 16 }}>
      <div style={{ fontSize: 14, fontWeight: 700, marginBottom: 8 }}>
        Recommended Actions
      </div>
      <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
        {recs.map((r, i) => (
          <li key={i} style={{ marginBottom: 10, paddingLeft: 8, borderLeft: `3px solid ${priorityColor(r.priority)}` }}>
            <div style={{ fontSize: 13, fontWeight: 600 }}>✓ {r.action}</div>
            <div style={{ fontSize: 12, color: "#666" }}>{r.reason}</div>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default RecommendationsPanel;
