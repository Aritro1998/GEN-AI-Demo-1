import { motion } from "framer-motion";
import { Menu, X } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { ModeToggle } from "@/mode-toggle";
import { Link, useNavigate } from "react-router-dom";
import useUserStore from "@/store/useUserStore";

interface NavbarProps {
  onMenuClick: () => void;
}

export const Navbar = ({ onMenuClick }: NavbarProps) => {
  const [isScrolled, setIsScrolled] = useState(false);
  const {user} = useUserStore()

  const navigate = useNavigate();

  useState(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  });

  return (
    <motion.nav
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.5 }}
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled
          ? "bg-background/80 backdrop-blur-xl border-b border-border shadow-glow-primary"
          : "bg-transparent"
      }`}
    >
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="flex items-center space-x-2"
          >
            <div className="w-8 h-8 rounded-lg bg-primary shadow-glow-primary" />
            <span className="text-xl font-bold bg-primary bg-clip-text text-transparent">
              🌿 AgroSense AI
            </span>
          </motion.div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="hidden md:flex items-center space-x-8"
          >
            {user?.role ==="Farmer" ?  ["Home", "Diagnose", "History"].map(
              (item, index) => (
                <Link
                  key={item}
                  to={`${item.toLowerCase()}`}
                  className="text-foreground/70 hover:text-primary transition-colors relative group"
                >
                  {item}
                  <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-primary transition-all duration-300 group-hover:w-full" />
                </Link>
              )
            ):["Home", "History"].map(
              (item, index) => (
                <Link
                  key={item}
                  to={`${item.toLowerCase()}`}
                  className="text-foreground/70 hover:text-primary transition-colors relative group"
                >
                  {item}
                  <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-primary transition-all duration-300 group-hover:w-full" />
                </Link>
              )
            )}
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.5 }}
            className="flex items-center space-x-4"
          >
            <Button
              onClick={() => navigate("/login")}
              variant="ghost"
              className="hidden md:inline-flex"
            >
              Sign In
            </Button>
            <Button className="hidden md:inline-flex bg-primary hover:shadow-glow-primary transition-all">
              Get Started
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={onMenuClick}
              className="md:hidden"
            >
              <Menu className="h-6 w-6" />
            </Button>
            <ModeToggle />
          </motion.div>
        </div>
      </div>
    </motion.nav>
  );
};
