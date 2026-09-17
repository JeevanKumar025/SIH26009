import { useEffect, useState } from "react";

function riskColor(level) {
  if (level === "HIGH") return "#dc2626";
  if (level === "MEDIUM") return "#d97706";
  return "#16a34a";
}

function RiskPanel() {
  const [risk, setRisk] = useState(null);

  useEffect(() => {
    fetch("http://localhost:8000/api/risk")
      .then(r => r.json())
      .then(setRisk);
  }, []);

  if (!risk) return <p>Loading risk data...</p>;

  const { summary, contributors } = risk;

  return (
    <div style={{ border: "1px solid #ddd", borderRadius: 8, padding: 16 }}>
      <div style={{ fontSize: 14, fontWeight: 700, marginBottom: 8 }}>
        Shortfall Risk
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 12 }}>
        <div style={{
          padding: "4px 12px", borderRadius: 6, color: "#fff",
          background: riskColor(summary.risk_level), fontWeight: 700, fontSize: 13
        }}>
          {summary.risk_level}
        </div>
        <div style={{ fontSize: 13, color: "#444" }}>
          {summary.shortfall_probability_pct}% shortfall probability &middot; {summary.shortfall_t} T predicted shortfall
        </div>
      </div>

      <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 6 }}>Main causes</div>
      <ul style={{ margin: 0, paddingLeft: 18 }}>
        {contributors.map((c, i) => (
          <li key={i} style={{ fontSize: 13, marginBottom: 4 }}>
            ⚠ {c.cause} — {c.contribution_pct.toFixed(1)}%
          </li>
        ))}
      </ul>
    </div>
  );
}

export default RiskPanel;