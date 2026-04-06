import { motion, AnimatePresence } from "framer-motion";
import { X, Home, Zap, Users, Mail, Settings } from "lucide-react";
import { Button } from "@/components/ui/button";

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

const menuItems = [
  { icon: Home, label: "Home", href: "#home" },
  { icon: Zap, label: "Features", href: "#features" },
  { icon: Users, label: "About", href: "#about" },
  { icon: Mail, label: "Contact", href: "#contact" },
  { icon: Settings, label: "Settings", href: "#settings" },
];

export const Sidebar = ({ isOpen, onClose }: SidebarProps) => {
  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50"
            onClick={onClose}
          />
          <motion.aside
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", damping: 25, stiffness: 200 }}
            className="fixed right-0 top-0 bottom-0 w-80 bg-card border-l border-border z-50 shadow-glow-primary"
          >
            <div className="flex flex-col h-full">
              <div className="flex items-center justify-between p-6 border-b border-border">
                <h2 className="text-xl font-bold bg-primary bg-clip-text text-transparent">
                  Navigation
                </h2>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={onClose}
                  className="hover:bg-muted"
                >
                  <X className="h-5 w-5" />
                </Button>
              </div>

              <nav className="flex-1 p-6 space-y-2">
                {menuItems.map((item, index) => (
                  <motion.a
                    key={item.label}
                    href={item.href}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-center space-x-3 px-4 py-3 rounded-lg hover:bg-muted transition-colors group"
                    onClick={onClose}
                  >
                    <item.icon className="h-5 w-5 text-muted-foreground group-hover:text-primary transition-colors" />
                    <span className="text-foreground group-hover:text-primary transition-colors">
                      {item.label}
                    </span>
                  </motion.a>
                ))}
              </nav>

              <div className="p-6 border-t border-border space-y-3">
                <Button className="w-full" variant="outline">
                  Sign In
                </Button>
                <Button className="w-full bg-primary hover:shadow-glow-primary transition-all">
                  Get Started
                </Button>
              </div>
            </div>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
};
