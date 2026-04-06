import { Features } from "@/components/Feature";
import { Footer } from "@/components/Footer/Footer";
import { Hero } from "@/components/Hero/hero";
import { Navbar } from "@/components/Navbar/navbar";
import { Sidebar } from "@/components/Sidebar/Sidebar";
import React, { useState } from "react";
import {motion} from "framer-motion"
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import Spline from "@splinetool/react-spline"
const HomePage = () => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-background text-foreground">
      

      {/* Hero Section */}
      <section className="flex flex-col md:flex-row  items-center px-8 mt-16 md:mt-24">

        {/* LEFT TEXT */}
        <motion.div
          initial={{ opacity: 0, x: -40 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6 }}
          className="flex-1"
        >
          <h2 className="text-5xl font-bold tracking-tight mb-6">
            Smart Crop Disease Detection
            <span className="text-primary"> Powered by AI</span>
          </h2>

          <p className="text-lg text-muted-foreground mb-8 max-w-xl">
            Upload a leaf image and instantly get disease diagnosis, severity
            assessment, and personalized advisory for your farm.
          </p>

          <Link to="/diagnose">
            <Button className="bg-primary text-primary-foreground px-6 py-5 rounded-lg text-lg shadow-sm hover:opacity-90">
              Start Detection →
            </Button>
          </Link>
        </motion.div>

        {/* RIGHT — 3D Spline Plant */}
         <div className="flex-1 relative h-[420px] md:h-[520px] w-full mt-10 md:mt-0 ml-12">

          {/* Soft overlay to blend spline with background */}
          <div className="absolute inset-0 z-[1] pointer-events-none 
                        bg-gradient-to-b from-background/20 via-background/10 to-background/50
                        rounded-xl" />

          <div className="h-full w-full rounded-xl overflow-hidden">
            <Spline
              scene="https://prod.spline.design/0cRi95FACRSF8TqO/scene.splinecode"
              className="h-full w-full 
                         opacity-90 
                         brightness-100 
                         contrast-95 
                         saturate-90 
                         backdrop-blur-sm"
            />
          </div>
          </div>
      </section>
    </div>
  );
};

export default HomePage;
