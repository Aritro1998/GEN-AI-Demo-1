import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import MapView from "@/components/MapView/MapView";
import ServerityGauge from "@/components/ServerityGauge/ServerityGauge";
import RequestsBarChart from "@/components/Chats/RequestsBarChart";
import { useState } from "react";

// Dummy data for dashboard
const stats = [
  { label: "Total Requests", value: 1240 },
  { label: "Farmers Registered", value: 320 },
  { label: "Prediction Accuracy", value: "91%" },
];

const topPlants = [
  { name: "Wheat", requests: 410 },
  { name: "Rice", requests: 320 },
  { name: "Corn", requests: 210 },
];

const weatherPrediction = {
  temperature: "28°C",
  humidity: "65%",
  rainfall: "12mm",
  summary: "Mild rain expected, moderate temperature."
};

const requestHotspots = [
  { lat: 28.6139, lng: 77.2090, city: "Delhi", count: 210 },
  { lat: 19.0760, lng: 72.8777, city: "Mumbai", count: 180 },
  { lat: 13.0827, lng: 80.2707, city: "Chennai", count: 120 },
  { lat: 22.5726, lng: 88.3639, city: "Kolkata", count: 150 },
  { lat: 12.9716, lng: 77.5946, city: "Bangalore", count: 160 },
  { lat: 23.0225, lng: 72.5714, city: "Ahmedabad", count: 90 },
  { lat: 17.3850, lng: 78.4867, city: "Hyderabad", count: 110 },
  { lat: 26.9124, lng: 75.7873, city: "Jaipur", count: 80 },
  { lat: 21.1702, lng: 72.8311, city: "Surat", count: 70 },
  { lat: 18.5204, lng: 73.8567, city: "Pune", count: 95 },
  { lat: 25.3176, lng: 82.9739, city: "Varanasi", count: 60 },
  { lat: 11.0168, lng: 76.9558, city: "Coimbatore", count: 55 },
  { lat: 15.2993, lng: 74.1240, city: "Goa", count: 50 },
  { lat: 27.1767, lng: 78.0081, city: "Agra", count: 65 },
  { lat: 30.7333, lng: 76.7794, city: "Chandigarh", count: 75 },
  { lat: 24.5854, lng: 73.7125, city: "Udaipur", count: 45 },
  { lat: 22.7196, lng: 75.8577, city: "Indore", count: 85 },
  { lat: 34.0837, lng: 74.7973, city: "Srinagar", count: 40 },
  { lat: 23.2599, lng: 77.4126, city: "Bhopal", count: 90 },
  { lat: 9.9312, lng: 76.2673, city: "Kochi", count: 70 },
];

export default function AdminDashboard() {
  return (
    <div className="flex flex-col gap-8 w-full max-w-6xl mx-auto py-8">
      {/* Top Grid Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
        {stats.map((stat, i) => (
          <Card key={i} className="w-full text-center">
            <CardHeader>
              <CardTitle className="text-lg">{stat.label}</CardTitle>
            </CardHeader>
            <CardContent>
              <span className="text-3xl font-bold">{stat.value}</span>
            </CardContent>
          </Card>
        ))}
      </div>
      {/* Requests Bar Chart */}
      <Card className="w-full">
        <CardHeader>
          <CardTitle>Requests Submitted Over Time</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <RequestsBarChart />
        </CardContent>
      </Card>
      {/* Map View */}
      <Card className="w-full">
        <CardHeader>
          <CardTitle>Request Hotspots Map</CardTitle>
        </CardHeader>
        <CardContent>
          <MapView hotspots={requestHotspots} />
        </CardContent>
      </Card>
      {/* Weather Prediction & Top Plant Requests */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="w-full">
          <CardHeader>
            <CardTitle>Upcoming Weather Prediction</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col gap-2">
              <span>Temperature: <b>{weatherPrediction.temperature}</b></span>
              <span>Humidity: <b>{weatherPrediction.humidity}</b></span>
              <span>Rainfall: <b>{weatherPrediction.rainfall}</b></span>
              <span className="text-muted-foreground">{weatherPrediction.summary}</span>
            </div>
          </CardContent>
        </Card>
        <Card className="w-full">
          <CardHeader>
            <CardTitle>Top Plant Prediction Requests</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {topPlants.map((plant, i) => (
                <li key={i} className="flex justify-between">
                  <span>{plant.name}</span>
                  <span className="font-bold text-primary">{plant.requests}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}