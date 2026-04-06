export function Particles() {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {Array.from({ length: 18 }).map((_, i) => (
        <div
          key={i}
          className={`
            particle absolute w-1 h-1 rounded-full bg-white/40 blur-[1px]
            left-[${Math.random() * 100}%]
            top-[${Math.random() * 100}%]
            particle-delay-${i % 3}
          `}
        />
      ))}
    </div>
  );
}
