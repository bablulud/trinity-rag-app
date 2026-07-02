import {
  AbsoluteFill,
  Img,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { COLORS } from "../theme";
import { fadeInOut, pop, reveal } from "../helpers";

export const Intro: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const opacity = fadeInOut(frame, durationInFrames, 8, 14);

  const logoScale = pop(frame, fps, 2);
  const logoY = interpolate(logoScale, [0, 1], [30, 0]);
  const textShift = interpolate(pop(frame, fps, 12), [0, 1], [24, 0]);
  const ruleW = reveal(frame, 22, 46);
  const taglineO = reveal(frame, 30, 48);

  return (
    <AbsoluteFill
      style={{
        opacity,
        alignItems: "center",
        justifyContent: "center",
        background: `radial-gradient(1200px 700px at 50% 42%, #ffffff 0%, #f3f6f7 70%, #eceff1 100%)`,
      }}
    >
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
        <Img
          src={staticFile("trinity-mark.png")}
          style={{
            width: 132,
            height: 132,
            objectFit: "contain",
            transform: `translateY(${logoY}px) scale(${logoScale})`,
          }}
        />
        <div
          style={{
            marginTop: 30,
            fontSize: 92,
            fontWeight: 700,
            letterSpacing: 1,
            color: COLORS.ink,
            transform: `translateY(${textShift}px)`,
          }}
        >
          Ask <span style={{ color: COLORS.slate }}>Trinity</span>
        </div>
        <div
          style={{
            height: 5,
            width: `${ruleW * 260}px`,
            background: COLORS.orange,
            borderRadius: 4,
            marginTop: 22,
          }}
        />
        <div
          style={{
            marginTop: 22,
            fontSize: 26,
            fontWeight: 600,
            letterSpacing: 7,
            color: COLORS.muted,
            opacity: taglineO,
          }}
        >
          RAIL KNOWLEDGE AGENT
        </div>
      </div>
    </AbsoluteFill>
  );
};
