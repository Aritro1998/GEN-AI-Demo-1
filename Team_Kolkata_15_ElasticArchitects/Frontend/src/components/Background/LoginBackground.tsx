import Spline from "@splinetool/react-spline";
export function LoginBackground() {
  return (
    <div className="absolute inset-0 w-full h-full overflow-hidden">
      <Spline
        scene="https://prod.spline.design/z35Tt0KTdVPyII8X/scene.splinecode"
        className="w-full h-full"
      />

      {/* Soft OKLCH overlay to brighten the background */}
      <div
        className="
        absolute inset-0 
        bg-[oklch(0.17_0.01_260)/0.35] 
        pointer-events-none
      "
      />

      {/* Light mist for legibility */}
      <div
        className="
        absolute inset-0 
        bg-gradient-to-b 
        from-[oklch(0.0_0_0)/0.15] 
        to-[oklch(0.0_0_0)/0.6]
        pointer-events-none
      "
      />
    </div>
  );
}
