"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ArrowUpRight, MapPin } from "lucide-react";
import { Link } from "react-router-dom";
import axiosInstance from "@/lib/axios";






export default function DiagnosisHistoryPage() {
  const [sortBy, setSortBy] = useState("date");
  const [diagnoseRecords, setDiagnoseRecords] = useState([
  {
    id: "1",
    timestamp: "2025-02-02 14:21",
    crop_name: "Tomato",
    image_path:"",
    latitude:"",
    longitude:"",
    diagnosis: "Early Blight",
    temperature: 68,
  },
 
]);
const [isLoading, setIsLoading] = useState(false);


const getAllDiagnoseRecords = async () => {
    setIsLoading(true)
  try {
    const response = await axiosInstance.get("/api/disease-files/");
    if(response.status === 200){
        setDiagnoseRecords(response.data);

    }
  } catch (error) {
    console.error("Error fetching diagnosis records:", error);
  }finally{
    setIsLoading(false)
  }
}

useEffect(()=>{
    getAllDiagnoseRecords()
},[])

console.log(diagnoseRecords)


  const sortedRecords = [...diagnoseRecords].sort((a, b) => {
    if (sortBy === "date") {
      return new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime();
    } else if (sortBy === "crop") {
      return a.crop_name.localeCompare(b.crop_name);
    }
    return 0;
  });

  const severityColor = (sev: number) => {
    if (sev >= 75) return "bg-destructive text-destructive-foreground";
    if (sev >= 50) return "bg-orange-500 text-white";
    if (sev >= 25) return "bg-primary text-primary-foreground";
    return "bg-green-600 text-white";
  };

  return (
    <div className="min-h-screen px-6 py-10 max-w-4xl mx-auto text-foreground">

      <h1 className="text-3xl font-bold text-primary mb-6">Previous Diagnoses</h1>

      <Card className="border-border shadow-sm bg-card">
        <CardHeader className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <CardTitle className="text-xl">Diagnosis History</CardTitle>

          {/* Sort Dropdown */}
          <div className="flex items-center gap-3">
            <span className="text-sm text-muted-foreground">Sort by:</span>
            <Select value={sortBy} onValueChange={(v) => setSortBy(v)}>
              <SelectTrigger className="w-[140px]">
                <SelectValue placeholder="Sort" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="date">Date</SelectItem>
                <SelectItem value="crop">Crop</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardHeader>

        <CardContent className="space-y-4">
          {sortedRecords.map((record) => (
            <Link key={record.id} to={`/diagnose/${record.id}`}>
              <div className="p-4 border mt-4 border-border rounded-lg bg-muted hover:bg-accent transition-colors cursor-pointer flex flex-col md:flex-row md:items-center justify-between gap-4">

                <div className="space-y-1 flex flex-col  items-start">
                  <h2 className="text-lg font-semibold">
                    {record.crop_name} — {record.diagnosis}
                  </h2>

                  <p className="text-xs text-muted-foreground ml-6">
                    {record.timestamp}
                  </p>

                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <MapPin size={14} />
                    {record.longitude}, {record.latitude}
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  <Badge className={`${severityColor(record.temperature)} px-3 py-1`}>
                    {record.temperature}% Severity
                  </Badge>

                  <ArrowUpRight className="text-primary" />
                </div>

              </div>
            </Link>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
