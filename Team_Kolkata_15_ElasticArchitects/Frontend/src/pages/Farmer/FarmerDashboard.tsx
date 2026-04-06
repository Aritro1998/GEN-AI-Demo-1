"use client";

import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Cloud, AlertTriangle, Leaf } from "lucide-react";
import { Link } from "react-router-dom";

export default function FarmerDashboard() {
  // Fake data for last 3 diagnoses
  const diagnoses = [
    {
      id: 1,
      plant: "Tomato Leaf",
      disease: "Early Blight",
      severity: "Moderate",
      date: "2025-02-03",
    },
    {
      id: 2,
      plant: "Potato Leaf",
      disease: "Late Blight",
      severity: "Severe",
      date: "2025-02-01",
    },
    {
      id: 3,
      plant: "Cabbage Leaf",
      disease: "Black Rot",
      severity: "Low",
      date: "2025-01-29",
    },
  ];

  return (
    <div className="min-h-screen px-6 py-10 bg-background text-foreground max-w-5xl mx-auto">

      {/* Title */}
      <h1 className="text-3xl font-bold mb-6 text-primary">
        Welcome Farmer 👨‍🌾
      </h1>

      {/* GRID LAYOUT */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* ---- DIAGNOSE NEW PLANT ---- */}
        <Card className="lg:col-span-3 border-border shadow-sm bg-card">
          <CardContent className="py-10 flex flex-col items-center justify-center">
            <Leaf className="w-14 h-14 text-primary mb-4" />
            <h2 className="text-xl font-semibold mb-3">Diagnose New Plant</h2>

            <p className="text-muted-foreground text-center mb-6 max-w-md">
              Upload a leaf image to detect plant disease instantly using AI.
            </p>

            <Link to="/diagnose">
              <Button className="bg-primary text-primary-foreground px-6 py-5 text-lg rounded-lg">
                Diagnose Now →
              </Button>
            </Link>
          </CardContent>
        </Card>

        {/* ---- LAST 3 DIAGNOSES ---- */}
        <Card className="border-border shadow-sm lg:col-span-2 bg-card">
          <CardHeader>
            <CardTitle className="text-lg">Last 3 Diagnoses</CardTitle>
          </CardHeader>

          <CardContent className="space-y-4">
            {diagnoses.map((item) => (
              <div
                key={item.id}
                className="p-4 rounded-lg bg-muted hover:bg-secondary transition border border-border"
              >
                <div className="flex justify-between items-center">
                  <div>
                    <p className="font-semibold">{item.plant}</p>
                    <p className="text-sm text-muted-foreground">{item.date}</p>
                  </div>

                  <div className="text-right">
                    <p className="font-medium text-primary">{item.disease}</p>
                    <p
                      className={`text-sm ${
                        item.severity === "Severe"
                          ? "text-destructive"
                          : item.severity === "Moderate"
                          ? "text-orange-600"
                          : "text-green-700"
                      }`}
                    >
                      {item.severity} Severity
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* ---- WEATHER ALERT / STATUS ---- */}
        <Card className="border-border shadow-sm bg-card">
          <CardHeader>
            <CardTitle className="text-lg">Local Weather Status</CardTitle>
          </CardHeader>

          <CardContent className="space-y-4">
            <div className="flex items-center gap-4">
              <Cloud className="w-10 h-10 text-primary" />
              <div>
                <p className="text-xl font-semibold">26°C — Cloudy</p>
                <p className="text-muted-foreground text-sm">
                  Good conditions for fungal diseases. Stay alert.
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3 bg-destructive/10 p-3 rounded-lg">
              <AlertTriangle className="w-5 h-5 text-destructive" />
              <p className="text-destructive text-sm">
                High humidity expected — chances of blight increasing.
              </p>
            </div>
          </CardContent>
        </Card>

      </div>
    </div>
  );
}
