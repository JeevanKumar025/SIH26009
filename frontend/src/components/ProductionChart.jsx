import { useEffect, useState } from "react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from "recharts";

function ProductionChart() {
  const [history, setHistory] = useState([]);
  const [forecast, setForecast] = useState(null);

  useEffect(() => {
    fetch("http://localhost:8000/api/production")
      .then(r => r.json())
      .then(data => {
        setHistory(data.history);
        setForecast(data.forecast);
      });
  }, []);

  if (history.length === 0) return <p>Loading production data...</p>;

  return (
    <div style={{ border: "1px solid #ddd", borderRadius: 8, padding: 16 }}>
      <div style={{ fontSize: 14, fontWeight: 700, marginBottom: 8 }}>
        Production: Actual vs Target (last 60 days)
      </div>

      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={history}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" tick={{ fontSize: 10 }} minTickGap={20} />
          <YAxis tick={{ fontSize: 10 }} />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="actual_production_t" stroke="#2563eb" name="Actual" dot={false} strokeWidth={2} />
          <Line type="monotone" dataKey="target_production_t" stroke="#9ca3af" name="Target" dot={false} strokeDasharray="4 4" />
        </LineChart>
      </ResponsiveContainer>

      {forecast && (
        <div style={{ marginTop: 8, fontSize: 13, color: "#444" }}>
          Next-period prediction: <b>{forecast.predicted_production_t} T</b>
          {" "}(Target: {forecast.target_production_t} T,
          Expected shortfall: {forecast.expected_shortfall_t} T)
        </div>
      )}
    </div>
  );
}

export default ProductionChart;