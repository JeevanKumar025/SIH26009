import { useEffect, useState } from "react";
import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet";

function color(p) {
  if (p >= 0.7) return "red";
  if (p >= 0.4) return "orange";
  return "green";
}

function ReserveMap({ mineId, mine }) {
  const [points, setPoints] = useState([]);

  useEffect(() => {
    fetch(`http://localhost:8000/api/reserve-map?mine_id=${mineId}`).then(r => r.json()).then(setPoints);
  }, [mineId]);

  if (points.length === 0) return <p>Loading map...</p>;

  return (
  <div style={{ height: 400, width: "100%" }}>
    <MapContainer key={mineId} center={[mine.lat, mine.lon]} zoom={13} style={{ height: "100%", width: "100%" }}>
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      {points.map((p, i) => (
        <CircleMarker
          key={i}
          center={[p.latitude, p.longitude]}
          radius={3}
          pathOptions={{ color: color(p.manganese_probability), fillOpacity: 0.7 }}
        >
          <Popup>{p.risk_class} ({(p.manganese_probability * 100).toFixed(0)}%)</Popup>
        </CircleMarker>
      ))}
    </MapContainer>
  </div>
);
}

export default ReserveMap;
