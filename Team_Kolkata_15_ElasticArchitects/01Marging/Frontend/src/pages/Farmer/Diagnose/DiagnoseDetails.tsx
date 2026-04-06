"use client";

import MapView from "@/components/MapView/MapView";
import SeverityGauge from "@/components/ServerityGauge/ServerityGauge";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import axiosInstance from "@/lib/axios";
import { MapPin } from "lucide-react";
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";



export default function DiagnosisDetailsPage() {
    const { id } = useParams()
    const [isLoading, setIsLoading] = useState(false);



    const [diagnosisRecord, setDiagnoseRecord] = useState({
        crop_name: "Tomato Leaf",
        image_path: "Early Blight",
        latitude: "68",
        longitude: "High",
        notes:"",
        soil_moisture: "",
        temperature: 0,
        soil_ph:"",
        soil_temperature:"",
        uv_index:"",
        upload_dt:"2025-02-04",
    })


    const getDiagnosisRecord = async()=>{
        setIsLoading(true)
        try {
            const res = await axiosInstance.get(`/api/disease-files/${id}`);
            if(res.status === 200){
                setDiagnoseRecord(res.data)
            }
        } catch (error) {
            console.log("Error fetching diagnosis record: ", error);
        }finally{
            setIsLoading(false)
        }
    }

    useEffect(()=>{
        getDiagnosisRecord()
    },[id])

    console.log(diagnosisRecord)
    

    const riskColor = {
        Low: "bg-green-600 text-white",
        Moderate: "bg-primary text-primary-foreground",
        High: "bg-orange-500 text-white",
        Severe: "bg-destructive text-destructive-foreground",
    };

    return (
        <div className="min-h-screen px-6 py-10 max-w-4xl mx-auto text-foreground">

            <h1 className="text-3xl font-bold text-primary mb-6">Diagnosis details for {diagnosisRecord.crop_name}</h1>

            <Card className="border-border shadow-sm bg-card">

                {/* Header */}
                <CardHeader>
                    <CardTitle className="text-2xl font-bold">
                        {diagnosisRecord.crop_name}
                    </CardTitle>
                    <p className="text-muted-foreground text-sm">
                        Crop: <span className="font-medium">{diagnosisRecord.crop_name}</span>
                    </p>
                    <p className="text-muted-foreground text-sm">
                        Date: {diagnosisRecord.upload_dt}
                    </p>
                </CardHeader>

                <CardContent className="space-y-10">

                    {/* Severity Section */}
                    <div className="flex flex-col md:flex-row items-center gap-10">
                        <div className="space-y-4 flex flex-row justify-between gap-8 items-center w-full ">
                            <SeverityGauge value={diagnosisRecord.temperature} />
                            <div className="w-full max-w-sm h-40 rounded-lg overflow-hidden border border-border shadow-sm bg-muted">
                                    <img
                                        src={diagnosisRecord.image_path || "/leaf.webp"}
                                        alt="Plant Uploaded"
                                        className="w-full h-full object-cover"
                                    />
                                </div>
                            <div className="flex flex-col gap-4 items-center justify-center">

                                <h3 className="text-lg font-semibold">Soil Moisture</h3>
                                <Badge className={` px-4 py-2 text-md`}>
                                    {diagnosisRecord.soil_moisture}
                                </Badge>

            

                                <MapPin size={18} />
                                <span>
                                    {diagnosisRecord.latitude}, {diagnosisRecord.longitude}
                                </span>
                            </div>
                            
                        </div>
                    </div>


                    {/* Action Plan */}
                    {/* <div className="space-y-4">
                        <h3 className="text-lg font-semibold">Recommended Action Plan</h3>

                        <div className="bg-muted p-5 rounded-lg border border-border space-y-3">
                            {diagnosisRecord.action_plan.map((item, index) => (
                                <div key={index} className="flex items-start gap-3">
                                    <div className="mt-1 h-2 w-2 rounded-full bg-primary" />
                                    <p className="text-sm">{item}</p>
                                </div>
                            ))}
                        </div>
                    </div> */}

                    {/* Map section */}

                    <div className="w-full space-y-4 ">
                        <h3 className="text-lg font-semibold">Location</h3>

                        <MapView longitude={diagnosisRecord.longitude} latitude={diagnosisRecord.latitude} />
                    </div>

                </CardContent>
            </Card>
        </div>
    );
}
