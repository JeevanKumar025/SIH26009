import SummaryCards from "./components/SummaryCards";
import ReserveMap from "./components/ReserveMap";
import ProductionChart from "./components/ProductionChart";
import RiskPanel from "./components/RiskPanel";
import RecommendationsPanel from "./components/RecommendationsPanel";
import "leaflet/dist/leaflet.css";

function App() {
  return (
    <div style={{ padding: 24, fontFamily: "sans-serif", maxWidth: 1200, margin: "0 auto" }}>
      <header style={{ marginBottom: 20 }}>
        <h1 style={{ margin: 0, fontSize: 24 }}>VantaWenge</h1>
        <p style={{ margin: 0, color: "#666" }}>
          Manganese Intelligence & Production Planning System
        </p>
      </header>

      <SummaryCards />

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginTop: 20 }}>
        <ReserveMap />
        <ProductionChart />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginTop: 16 }}>
        <RiskPanel />
        <RecommendationsPanel />
      </div>
    </div>
  );
}

export default App;