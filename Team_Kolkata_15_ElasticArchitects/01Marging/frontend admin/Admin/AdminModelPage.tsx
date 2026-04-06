import { Card, CardHeader, CardTitle, CardAction, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import AccuracyLineChart from "@/components/Chats/AccuracyLineChart";
import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogFooter, DialogTitle } from "@/components/ui/dialog";

export default function AdminModelPage() {
  const [open, setOpen] = useState(false);

  // Example model details
  const model = {
    name: "CNN Model",
    accuracy: 0.90,
    lastTrained: "2025-11-20",
  };

  return (
    <div className="flex flex-col gap-6 w-full max-w-3xl mx-auto py-8">
      {/* Model Details Box */}
      <Card className="w-full">
        <CardHeader className="flex flex-row justify-between items-center">
          <CardTitle className="w-full">
            <span className="flex flex-row gap-2 items-center text-base font-semibold">
              {model.name} <span className="mx-2">|</span>
              Accuracy: <span className="font-bold text-green-600">{(model.accuracy * 100).toFixed(2)}%</span> <span className="mx-2">|</span>
              Last trained: {model.lastTrained}
            </span>
          </CardTitle>
          <CardAction>
            <Button variant="outline" onClick={() => setOpen(true)}>Retrain Model</Button>
          </CardAction>
        </CardHeader>
      </Card>
      {/* Chart Box */}
      <Card className="w-full">
        <CardHeader>
          <CardTitle>Accuracy Over Epochs</CardTitle>
        </CardHeader>
        <CardContent>
          <AccuracyLineChart />
        </CardContent>
      </Card>
      {/* Retrain Modal */}
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Retrain Model</DialogTitle>
          </DialogHeader>
          <div className="flex flex-col gap-4 py-4">
            <label htmlFor="trainFile" className="font-medium">Select Training File</label>
            <input type="file" id="trainFile" className="border rounded px-3 py-2" />
          </div>
          <DialogFooter>
            <Button onClick={() => setOpen(false)} variant="outline">Cancel</Button>
            <Button className="ml-2">Start Training</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}