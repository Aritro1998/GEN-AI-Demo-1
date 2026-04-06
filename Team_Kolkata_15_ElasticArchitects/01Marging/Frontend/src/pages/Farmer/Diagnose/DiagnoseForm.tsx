"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Camera, CloudCog, ImageIcon, MapPin, Rss } from "lucide-react";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import axiosInstance from "@/lib/axios";
import { toast } from "sonner";

export default function DiagnoseForm() {
    const [image, setImage] = useState<string | null>(null);
    const [location, setLocation] = useState({ lat: "", lng: "" });
    const [loadingLocation, setLoadingLocation] = useState(false);
    const [loading, setLoading] = useState(false)
    // NEW FORM STATE
    const [formData, setFormData] = useState({
        cropName: "",
        weather: "hot",
        temperature: "",
        soilMoisture: "",
        soilTemperature: "",
        soilPh: "",
        uvIndex: "",
        notes: "",
    });


    const handleSubmit = async () => {
        try {
            setLoading(true)
            const res = await axiosInstance.post("/api/disease-files/", {
                crop_name: formData.cropName,
                image_path: image,
                latitude: location.lat,
                longitude: location.lng,
                notes: formData.notes,
                weather: formData.weather,
                temperature: formData.temperature,
                soil_moisture: formData.soilMoisture,
                soil_ph: formData.soilPh,
                uv_index: formData.uvIndex,
                upload_dt: Date.now().toLocaleString
            })

            if (res.status === 201) {
                setFormData({
                    cropName: "",
                    weather: "hot",
                    temperature: "",
                    soilMoisture: "",
                    soilTemperature: "",
                    soilPh: "",
                    uvIndex: "",
                    notes: "",
                });
                setImage("")
                setLocation({ lat: "", lng: "" })
                toast.success("Disease submitted.")
            }
        } catch (error) {
            console.log(error)
        } finally {
            setLoading(false)
        }

    }

    // AUTO-DETECT LOCATION
    const detectLocation = () => {
        if (!navigator.geolocation) {
            alert("Geolocation is not supported.");
            return;
        }

        setLoadingLocation(true);

        navigator.geolocation.getCurrentPosition(
            (pos) => {
                setLocation({
                    lat: pos.coords.latitude.toFixed(6),
                    lng: pos.coords.longitude.toFixed(6),
                });
                setLoadingLocation(false);
            },
            () => {
                alert("Unable to retrieve location.");
                setLoadingLocation(false);
            }
        );
    };

    // IMAGE HANDLER
    const handleFileUpload = (file: File | null) => {
        if (!file) return;

        const reader = new FileReader();
        reader.onload = () => setImage(reader.result as string);
        reader.readAsDataURL(file);
    };

    return (
        <div className="min-h-screen bg-background text-foreground px-6 py-10 max-w-3xl mx-auto">
            <h1 className="text-3xl font-bold text-primary mb-6">Diagnose New Plant</h1>

            <Card className="shadow-sm border-border bg-card">
                <CardHeader>
                    <CardTitle>Plant Diagnosis Form</CardTitle>
                </CardHeader>

                <CardContent className="space-y-8">

                    {/* ---------------- IMAGE UPLOAD ---------------- */}
                    <div className="space-y-3">
                        <h2 className="text-lg font-semibold">1. Upload Image</h2>
                        <div className="h-60 border border-border rounded-lg flex items-center justify-center bg-muted overflow-hidden">
                            {image ? (
                                <img src={image} className="h-full w-full object-cover" />
                            ) : (
                                <p className="text-muted-foreground text-sm">No image selected</p>
                            )}
                        </div>
                        <div className="flex gap-4">
                            <label
                                htmlFor="cameraInput"
                                className="flex items-center gap-2 bg-primary text-primary-foreground px-4 py-3 rounded-lg cursor-pointer hover:opacity-90"
                            >
                                <Camera size={18} />
                                Use Camera
                            </label>
                            <input
                                id="cameraInput"
                                type="file"
                                accept="image/*"
                                capture="environment"
                                className="hidden"
                                onChange={(e) => handleFileUpload(e.target.files?.[0] || null)}
                            />

                            <label
                                htmlFor="fileInput"
                                className="flex items-center gap-2 bg-secondary text-secondary-foreground px-4 py-3 rounded-lg cursor-pointer hover:bg-accent"
                            >
                                <ImageIcon size={18} />
                                Upload from Gallery
                            </label>
                            <input
                                id="fileInput"
                                type="file"
                                accept="image/*"
                                className="hidden"
                                onChange={(e) => handleFileUpload(e.target.files?.[0] || null)}
                            />
                        </div>
                    </div>

                    {/* ---------------- LOCATION ---------------- */}
                    <div className="space-y-3">
                        <h2 className="text-lg font-semibold">2. Current Location</h2>
                        <div className="flex gap-4">
                            <div className="flex-1">
                                <label className="text-sm text-muted-foreground">Latitude</label>
                                <Input
                                    type="text"
                                    value={location.lat}
                                    onChange={(e) =>
                                        setLocation((prev) => ({ ...prev, lat: e.target.value }))
                                    }
                                />
                            </div>
                            <div className="flex-1">
                                <label className="text-sm text-muted-foreground">Longitude</label>
                                <Input
                                    type="text"
                                    value={location.lng}
                                    onChange={(e) =>
                                        setLocation((prev) => ({ ...prev, lng: e.target.value }))
                                    }
                                />
                            </div>
                        </div>
                        <Button
                            variant="outline"
                            className="flex items-center gap-2"
                            onClick={detectLocation}
                        >
                            <MapPin size={18} />
                            {loadingLocation ? "Detecting..." : "Auto-detect location"}
                        </Button>
                    </div>

                    {/* ---------------- NEW ENVIRONMENT FIELDS ---------------- */}
                    <div className="space-y-3">
                        <h2 className="text-lg font-semibold">3. Plant & Environment Details</h2>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

                            {/* Crop Name */}
                            <div className="flex flex-col items-start gap-2">
                                <label className="text-sm text-muted-foreground">Crop Name</label>
                                <Input
                                    value={formData.cropName}
                                    onChange={(e) =>
                                        setFormData((prev) => ({ ...prev, cropName: e.target.value }))
                                    }
                                    placeholder="e.g., Tomato"
                                />
                            </div>

                            {/* Weather Condition */}
                            <div className="flex  min-w-full flex-col items-start gap-2">
                                <label className="text-sm text-muted-foreground">Weather Condition</label>
                                <Select
                                    value={formData.weather}
                                    onValueChange={(v) =>
                                        setFormData((prev) => ({ ...prev, weather: v }))
                                    }

                                >
                                    <SelectTrigger className="w-full">
                                        <SelectValue placeholder="Select Weather" />
                                    </SelectTrigger>
                                    <SelectContent className="min-w-full">
                                        <SelectItem value="hot">Hot</SelectItem>
                                        <SelectItem value="cold">Cold</SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>

                            {/* Temperature */}
                            <div className="flex flex-col items-start gap-2">
                                <label className="text-sm text-muted-foreground">Temperature (°C)</label>
                                <Input
                                    type="number"
                                    value={formData.temperature}
                                    onChange={(e) =>
                                        setFormData((prev) => ({ ...prev, temperature: e.target.value }))
                                    }
                                />
                            </div>

                            {/* Soil Moisture */}
                            <div className="flex flex-col items-start gap-2">
                                <label className="text-sm text-muted-foreground">Soil Moisture (%)</label>
                                <Input
                                    type="number"
                                    value={formData.soilMoisture}
                                    onChange={(e) =>
                                        setFormData((prev) => ({ ...prev, soilMoisture: e.target.value }))
                                    }
                                />
                            </div>

                            {/* Soil Temperature */}
                            <div className="flex flex-col items-start gap-2">
                                <label className="text-sm text-muted-foreground">Soil Temperature (°C)</label>
                                <Input
                                    type="number"
                                    value={formData.soilTemperature}
                                    onChange={(e) =>
                                        setFormData((prev) => ({ ...prev, soilTemperature: e.target.value }))
                                    }
                                />
                            </div>

                            {/* Soil pH */}
                            <div className="flex flex-col items-start gap-2">
                                <label className="text-sm text-muted-foreground">Soil pH</label>
                                <Input
                                    type="number"
                                    step="0.1"
                                    value={formData.soilPh}
                                    onChange={(e) =>
                                        setFormData((prev) => ({ ...prev, soilPh: e.target.value }))
                                    }
                                />
                            </div>

                            {/* UV Index */}
                            <div className="flex flex-col items-start gap-2 w-full">
                                <label className="text-sm text-muted-foreground">UV Index</label>
                                <Input
                                    className="min-w-full"
                                    type="number"
                                    value={formData.uvIndex}
                                    onChange={(e) =>
                                        setFormData((prev) => ({ ...prev, uvIndex: e.target.value }))
                                    }
                                />
                            </div>

                        </div>
                    </div>

                    {/* ---------------- NOTES ---------------- */}
                    <div className="space-y-3">
                        <h2 className="text-lg font-semibold">4. Notes (Optional)</h2>
                        <Textarea
                            placeholder="Add any notes for this diagnosis..."
                            className="min-h-[100px]"
                            value={formData.notes}
                            onChange={(e) =>
                                setFormData((prev) => ({ ...prev, notes: e.target.value }))
                            }
                        />
                    </div>

                    {/* SUBMIT BUTTON */}
                    <Button
                        disabled={loading}
                        onClick={handleSubmit}
                        className="w-full bg-primary text-primary-foreground py-6 text-lg rounded-lg hover:opacity-90">
                        {loading ? "Analyzing..." : "Analyze Plant →"}
                    </Button>

                </CardContent>
            </Card>
        </div>
    );
}
