import { Label } from "@radix-ui/react-label";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { motion } from "framer-motion";
import { Input } from "../ui/input";
import { Button } from "../ui/button";

const LivePreviewCard: React.FC = () => (
  <motion.aside
    initial={{ opacity: 0, scale: 0.98 }}
    animate={{ opacity: 1, scale: 1 }}
    transition={{ duration: 0.6 }}
  >
    <Card className="backdrop-blur-md bg-white/3 border-white/6">
      <CardHeader>
        <CardTitle className="text-lg">Live Preview</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="rounded-xl overflow-hidden border border-white/6 p-4">
            <div className="text-sm opacity-80">Project name</div>
            <div className="mt-2 font-semibold">Aurora Dashboard</div>
            <p className="mt-3 text-xs opacity-70">
              Responsive admin dashboard with immersive 3D visuals.
            </p>
            <div className="mt-4">
              <Label className="text-xs">Invite teammates</Label>
              <div className="flex gap-2 mt-2">
                <Input placeholder="email@company.com" />
                <Button>Invite</Button>
              </div>
            </div>
          </div>

          <div className="rounded-xl overflow-hidden border border-white/6 p-4">
            <div className="text-xs opacity-70">Quick actions</div>
            <div className="mt-3 flex flex-col gap-2">
              <Button size="sm">New Project</Button>
              <Button size="sm" variant={"ghost" as any}>
                Duplicate
              </Button>
              <Button size="sm" variant={"link" as any}>
                Settings
              </Button>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  </motion.aside>
);

export default LivePreviewCard;
