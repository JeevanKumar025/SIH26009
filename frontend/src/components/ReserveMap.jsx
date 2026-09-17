import { useEffect, useMemo, useState } from "react";
import { MapContainer, TileLayer, ImageOverlay, useMapEvents } from "react-leaflet";

// Same thresholds used to derive risk_class (LOW/MEDIUM/HIGH) server-side.
function zoneColor(p) {
  if (p >= 0.7) return [220, 38, 38]; // red   - HIGH
  if (p >= 0.4) return [245, 158, 11]; // amber - MEDIUM
  return [22, 163, 74]; // green - LOW
}

function zoneLabel(p) {
  if (p >= 0.7) return "HIGH";
  if (p >= 0.4) return "MEDIUM";
  return "LOW";
}

// Builds a PNG data URL from the flattened probability grid: one solid
// pixel per grid cell, so adjacent same-zone cells merge visually into a
// continuous colored region instead of separate dot markers.
function gridToImageURL(grid) {
  const { nx, ny, probability } = grid;
  const canvas = document.createElement("canvas");
  canvas.width = nx;
  canvas.height = ny;
  const ctx = canvas.getContext("2d");
  const imgData = ctx.createImageData(nx, ny);

  for (let i = 0; i < probability.length; i++) {
    const [r, g, b] = zoneColor(probability[i]);
    const o = i * 4;
    imgData.data[o] = r;
    imgData.data[o + 1] = g;
    imgData.data[o + 2] = b;
    imgData.data[o + 3] = 200;
  }

  ctx.putImageData(imgData, 0, 0);
  return canvas.toDataURL();
}

// Finds the probability of the grid cell nearest a given lat/lon.
function sampleGrid(grid, lat, lon) {
  const { nx, ny, lat_min, lat_max, lon_min, lon_max, probability } = grid;
  if (lat < lat_min || lat > lat_max || lon < lon_min || lon > lon_max) return null;
  const col = Math.round(((lon - lon_min) / (lon_max - lon_min)) * (nx - 1));
  const row = Math.round(((lat_max - lat) / (lat_max - lat_min)) * (ny - 1));
  const idx = row * nx + col;
  return probability[idx] ?? null;
}

function HoverReadout({ grid, onHover }) {
  useMapEvents({
    mousemove(e) {
      const p = sampleGrid(grid, e.latlng.lat, e.latlng.lng);
      onHover(p === null ? null : { lat: e.latlng.lat, lon: e.latlng.lng, p });
    },
    mouseout() {
      onHover(null);
    },
  });
  return null;
}

function Legend() {
  const items = [
    { label: "HIGH (≥ 70%)", color: "rgb(220, 38, 38)" },
    { label: "MEDIUM (40–70%)", color: "rgb(245, 158, 11)" },
    { label: "LOW (< 40%)", color: "rgb(22, 163, 74)" },
  ];
  return (
    <div
      style={{
        position: "absolute",
        bottom: 10,
        left: 10,
        zIndex: 1000,
        background: "rgba(255,255,255,0.92)",
        borderRadius: 6,
        padding: "8px 10px",
        fontSize: 12,
        lineHeight: 1.6,
        boxShadow: "0 1px 4px rgba(0,0,0,0.2)",
      }}
    >
      <div style={{ fontWeight: 600, marginBottom: 4 }}>Manganese probability zone</div>
      {items.map((it) => (
        <div key={it.label} style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <span
            style={{
              width: 12,
              height: 12,
              borderRadius: 2,
              background: it.color,
              display: "inline-block",
            }}
          />
          {it.label}
        </div>
      ))}
    </div>
  );
}

function ReserveMap() {
  const [grid, setGrid] = useState(null);
  const [hover, setHover] = useState(null);

  useEffect(() => {
    fetch("http://localhost:8000/api/reserve-map")
      .then((r) => r.json())
      .then(setGrid);
  }, []);

  const imageUrl = useMemo(() => (grid ? gridToImageURL(grid) : null), [grid]);

  if (!grid || !imageUrl) return <p>Loading map...</p>;

  const bounds = [
    [grid.lat_min, grid.lon_min],
    [grid.lat_max, grid.lon_max],
  ];

  return (
    <div style={{ height: 400, width: "100%", position: "relative" }}>
      <MapContainer center={[21.55, 79.69]} zoom={13} style={{ height: "100%", width: "100%" }}>
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        <ImageOverlay url={imageUrl} bounds={bounds} opacity={0.65} />
        <HoverReadout grid={grid} onHover={setHover} />
      </MapContainer>
      <Legend />
      {hover && (
        <div
          style={{
            position: "absolute",
            top: 10,
            right: 10,
            zIndex: 1000,
            background: "rgba(255,255,255,0.92)",
            borderRadius: 6,
            padding: "6px 10px",
            fontSize: 12,
            boxShadow: "0 1px 4px rgba(0,0,0,0.2)",
          }}
        >
          <strong>{zoneLabel(hover.p)}</strong> zone · {(hover.p * 100).toFixed(0)}% probability
        </div>
      )}
    </div>
  );
}

export default ReserveMap;
