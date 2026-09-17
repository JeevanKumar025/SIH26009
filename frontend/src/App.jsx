import SummaryCards from "./components/SummaryCards";
import ReserveMap from "./components/ReserveMap";
import ProductionChart from "./components/ProductionChart";
import RiskPanel from "./components/RiskPanel";
import RecommendationsPanel from "./components/RecommendationsPanel";
import "leaflet/dist/leaflet.css";
import { useEffect, useState } from "react";

function App() {
  const [mines, setMines] = useState([]);
  const [mineId, setMineId] = useState("dongri_buzurg");
  useEffect(() => {
    fetch("http://localhost:8000/api/mines").then(r => r.json()).then(setMines);
  }, []);
  const mine = mines.find(item => item.id === mineId);
  return (
    <div style={{ padding: 24, fontFamily: "sans-serif", maxWidth: 1200, margin: "0 auto" }}>
      <header style={{ marginBottom: 20 }}>
        <h1 style={{ margin: 0, fontSize: 24 }}>VantaWenge</h1>
        <p style={{ margin: 0, color: "#666" }}>
          Manganese Intelligence & Production Planning System
        </p>
      </header>

      <section style={{ marginBottom: 16, padding: 12, background: "#f8fafc", borderRadius: 8 }}>
        <label htmlFor="mine" style={{ fontWeight: 700, marginRight: 10 }}>Mine</label>
        <select id="mine" value={mineId} onChange={e => setMineId(e.target.value)}>
          {mines.map(item => <option key={item.id} value={item.id}>{item.name}</option>)}
        </select>
        {mine && <span style={{ marginLeft: 10, fontSize: 13, color: mine.status === "active" ? "#166534" : "#92400e" }}>
          {mine.status === "active" ? "Processed prototype available" : "Awaiting mine-specific processing"}
        </span>}
        {mine && <div style={{ marginTop: 8, fontSize: 12, color: "#475569" }}>{mine.data_note}</div>}
      </section>

      {mine?.status !== "active" ? (
        <section style={{ border: "1px solid #f59e0b", background: "#fffbeb", borderRadius: 8, padding: 16 }}>
          <b>{mine?.name}</b> is registered but has no mine-specific dashboard data yet. Run the documented pipeline only after adding its real Sentinel-2 feature GeoTIFF; the app will not substitute Dongri Buzurg results.
        </section>
      ) : <div key={mineId}>

      <SummaryCards mineId={mineId} />

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginTop: 20 }}>
        <ReserveMap mineId={mineId} mine={mine} />
        <ProductionChart mineId={mineId} />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginTop: 16 }}>
        <RiskPanel mineId={mineId} />
        <RecommendationsPanel mineId={mineId} />
      </div>
      </div>}
    </div>
  );
}

export default App;
