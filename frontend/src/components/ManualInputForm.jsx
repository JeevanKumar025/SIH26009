import { useState } from "react";

function ManualInputForm({ onResult }) {
  const [form, setForm] = useState({
    downtime_hrs: "", blasting_delay_hrs: "", soil_moisture_pct: "", target_production_t: ""
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("http://localhost:8000/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          mine_id: "dongri_buzurg",
          downtime_hrs: parseFloat(form.downtime_hrs),
          blasting_delay_hrs: parseFloat(form.blasting_delay_hrs),
          soil_moisture_pct: parseFloat(form.soil_moisture_pct),
          target_production_t: parseFloat(form.target_production_t),
        }),
      });
      if (!res.ok) throw new Error("Prediction failed");
      onResult(await res.json());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ border: "1px solid #ddd", borderRadius: 8, padding: 16 }}>
      <div style={{ fontSize: 14, fontWeight: 700, marginBottom: 8 }}>Today's Operational Report</div>
      {["downtime_hrs", "blasting_delay_hrs", "soil_moisture_pct", "target_production_t"].map((field) => (
        <div key={field} style={{ marginBottom: 8 }}>
          <label style={{ fontSize: 12, color: "#666" }}>{field.replace(/_/g, " ")}</label>
          <input
            type="number" name={field} value={form[field]} onChange={handleChange} required
            style={{ width: "100%", padding: 6, borderRadius: 4, border: "1px solid #ccc" }}
          />
        </div>
      ))}
      <button type="submit" disabled={loading} style={{ padding: "8px 16px", borderRadius: 6 }}>
        {loading ? "Predicting..." : "Update Prediction"}
      </button>
      {error && <div style={{ color: "red", fontSize: 12, marginTop: 6 }}>{error}</div>}
    </form>
  );
}

export default ManualInputForm;