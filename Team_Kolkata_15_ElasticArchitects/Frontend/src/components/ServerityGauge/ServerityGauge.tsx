"use client";

type Props = {
  value: number; // severity %
};

export default function SeverityGauge({ value }: Props) {
  const radius = 60;
  const circumference = 2 * Math.PI * radius;
  const progress = ((100 - value) / 100) * circumference;

  let color = "stroke-green-600";
  if (value >= 75) color = "stroke-destructive";
  else if (value >= 50) color = "stroke-orange-500";
  else if (value >= 25) color = "stroke-primary";

  return (
    <div className="relative w-40 h-40 flex items-center justify-center">
      <svg className="w-full h-full transform -rotate-90">
        <circle
          cx="80"
          cy="80"
          r={radius}
          className="stroke-muted stroke-[12]"
          fill="transparent"
        />
        <circle
          cx="80"
          cy="80"
          r={radius}
          className={`${color} stroke-[12] transition-all duration-700`}
          fill="transparent"
          strokeDasharray={circumference}
          strokeDashoffset={progress}
          strokeLinecap="round"
        />
      </svg>

      <span className="absolute text-xl font-semibold text-foreground">
        {value}%
      </span>
    </div>
  );
}
