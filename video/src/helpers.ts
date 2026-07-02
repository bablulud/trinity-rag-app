import { interpolate, spring } from "remotion";

/** Ease a value in at the start and out at the end of a local sequence. */
export const fadeInOut = (
  frame: number,
  duration: number,
  fadeIn = 12,
  fadeOut = 12
): number => {
  return interpolate(
    frame,
    [0, fadeIn, duration - fadeOut, duration],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
};

/** A spring that settles quickly, good for entrances. */
export const pop = (frame: number, fps: number, delay = 0): number =>
  spring({
    frame: frame - delay,
    fps,
    config: { damping: 200, stiffness: 120, mass: 0.7 },
  });

/** Linear reveal 0->1 over [start, end]. */
export const reveal = (frame: number, start: number, end: number): number =>
  interpolate(frame, [start, end], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
