import React from "react";
import { MapContainer, TileLayer, Circle, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

// Fix default marker icon issue in Leaflet + Webpack
// @ts-ignore
if (L.Icon.Default.prototype._getIconUrl) {
  // @ts-ignore
  delete L.Icon.Default.prototype._getIconUrl;
}
L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

interface Hotspot {
  lat: number;
  lng: number;
  city: string;
  count: number;
}

const DEFAULT_CENTER = { lat: 22.9734, lng: 78.6569 }; // Center of India

function getColor(count: number) {
  if (count > 180) return "#d73027"; // red
  if (count > 140) return "#fc8d59"; // orange
  if (count > 100) return "#fee08b"; // yellow
  if (count > 80) return "#91cf60"; // green
  return "#4575b4"; // blue
}

const MapView = ({ hotspots = [] }: { hotspots?: Hotspot[] }) => {
  return (
    <MapContainer
      center={[DEFAULT_CENTER.lat, DEFAULT_CENTER.lng]}
      zoom={5}
      style={{ height: "300px", width: "100%" }}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {hotspots.map((spot, idx) => (
        <Circle
          key={idx}
          center={[spot.lat, spot.lng]}
          radius={spot.count * 1000} // scale radius by request count
          pathOptions={{ color: getColor(spot.count), fillColor: getColor(spot.count), fillOpacity: 0.5 }}
        >
          <Popup>
            <b>{spot.city}</b><br />Requests: {spot.count}
          </Popup>
        </Circle>
      ))}
    </MapContainer>
  );
};

export default MapView;