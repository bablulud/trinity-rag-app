export const COLORS = {
  slate: "#7a929b",
  orange: "#be4d00",
  orangeDark: "#a83f00",
  ink: "#23282b",
  muted: "#8a9296",
  line: "#e6e9eb",
  paper: "#ffffff",
  panel: "#f4f6f7",
  panelBorder: "#dfe3e6",
};

export const FPS = 30;
export const WIDTH = 1920;
export const HEIGHT = 1080;

export const SCENE = {
  intro: { from: 0, duration: 78 },
  problem: { from: 78, duration: 84 },
  pipeline: { from: 162, duration: 210 },
  features: { from: 372, duration: 210 },
  cta: { from: 582, duration: 108 },
};

export const TOTAL =
  SCENE.cta.from + SCENE.cta.duration;
