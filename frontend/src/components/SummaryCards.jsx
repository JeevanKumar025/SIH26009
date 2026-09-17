import { useEffect, useState } from "react";

function SummaryCards() {
  const [reserve, setReserve] = useState(null);
  const [risk, setRisk] = useState(null);

  useEffect(() => {
    fetch("http://localhost:8000/api/reserve").then(r => r.json()).then(setReserve);
    fetch("http://localhost:8000/api/risk").then(r => r.json()).then(setRisk);
  }, []);

  if (!reserve || !risk) return <p>Loading...</p>;

  return (
    <div style={{ display: "flex", gap: "16px" }}>
      <Card title="Reserve" value={`${reserve.high_zone_km2} km²`} />
      <Card title="Est. Tonnage" value={`${reserve.estimated_reserve_tonnes.toLocaleString()} T`} />
      <Card title="Shortfall" value={`${risk.summary.shortfall_t} T`} />
      <Card title="Risk" value={risk.summary.risk_level} highlight={risk.summary.risk_level === "HIGH"} />
      <Card title="Avg NDVI (High Zone)" value={reserve.avg_ndvi_high_zone} />
    </div>
  );
}

function Card({ title, value, highlight }) {
  return (
    <div style={{
      border: "1px solid #ddd", borderRadius: 8, padding: 16, minWidth: 140,
      background: highlight ? "#fee2e2" : "#fff"
    }}>
      <div style={{ fontSize: 12, color: "#666" }}>{title}</div>
      <div style={{ fontSize: 22, fontWeight: 700 }}>{value}</div>
    </div>
  );
}

export default SummaryCards;