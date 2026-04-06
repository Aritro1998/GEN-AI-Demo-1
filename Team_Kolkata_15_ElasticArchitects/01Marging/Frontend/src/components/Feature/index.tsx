import { motion } from "framer-motion";
import { Zap, Shield, Rocket, Globe, Cpu, Sparkles } from "lucide-react";

const features = [
  {
    icon: Zap,
    title: "Lightning Fast",
    description:
      "Optimized performance for blazing fast load times and smooth interactions.",
  },
  {
    icon: Shield,
    title: "Secure by Default",
    description:
      "Enterprise-grade security with end-to-end encryption and data protection.",
  },
  {
    icon: Rocket,
    title: "Scalable Infrastructure",
    description:
      "Built to grow with your needs, from startup to enterprise scale.",
  },
  {
    icon: Globe,
    title: "Global Reach",
    description:
      "Deploy worldwide with our distributed network and CDN integration.",
  },
  {
    icon: Cpu,
    title: "AI-Powered",
    description: "Leverage cutting-edge AI and machine learning capabilities.",
  },
  {
    icon: Sparkles,
    title: "Innovation First",
    description: "Stay ahead with continuous updates and new feature releases.",
  },
];

export const Features = () => {
  return (
    <section id="features" className="relative py-24 bg-background">
      <div className="absolute inset-0 bg-primary-glow opacity-20" />

      <div className="relative container mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            Powerful{" "}
            <span className="bg-primary bg-clip-text text-transparent">
              Features
            </span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Everything you need to build amazing digital experiences
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              whileHover={{ y: -5 }}
              className="group relative p-6 rounded-2xl bg-card border border-border hover:border-primary/50 transition-all hover:shadow-glow-primary"
            >
              <div className="absolute inset-0 bg-primary opacity-0 group-hover:opacity-5 rounded-2xl transition-opacity" />

              <div className="relative">
                <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4 group-hover:bg-primary/20 transition-colors">
                  <feature.icon className="h-6 w-6 text-primary" />
                </div>

                <h3 className="text-xl font-semibold mb-2 group-hover:text-primary transition-colors">
                  {feature.title}
                </h3>

                <p className="text-muted-foreground">{feature.description}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};
