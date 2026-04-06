"use client";
import { useState } from "react";

export function Parallax({ children }: { children: React.ReactNode }) {
  const [pos, setPos] = useState({ x: 0, y: 0 });

  return (
    <div
      onMouseMove={(e) => {
        const r = e.currentTarget.getBoundingClientRect();
        const x = (e.clientX - r.left - r.width / 2) / 40;
        const y = (e.clientY - r.top - r.height / 2) / 40;
        setPos({ x, y });
      }}
      onMouseLeave={() => setPos({ x: 0, y: 0 })}
      className="transition-all duration-300"
      style={{
        transform: `translate(${pos.x}px, ${pos.y}px)`,
      }}
    >
      {children}
    </div>
  );
}
