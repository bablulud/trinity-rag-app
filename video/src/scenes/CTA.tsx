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

const mono = "ui-monospace, Menlo, monospace";

export const CTA: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const opacity = fadeInOut(frame, durationInFrames, 10, 18);

  const logoS = pop(frame, fps, 2);
  const titleO = reveal(frame, 12, 26);
  const cmdO = pop(frame, fps, 30);
  const cmdY = interpolate(cmdO, [0, 1], [24, 0]);
  const urlO = reveal(frame, 46, 62);

  return (
    <AbsoluteFill
      style={{
        opacity,
        background: `radial-gradient(1200px 700px at 50% 45%, #ffffff 0%, #eef1f2 100%)`,
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <Img
        src={staticFile("trinity-mark.png")}
        style={{
          width: 96,
          height: 96,
          objectFit: "contain",
          transform: `scale(${logoS})`,
          opacity: logoS,
        }}
      />
      <div
        style={{
          marginTop: 24,
          fontSize: 72,
          fontWeight: 700,
          color: COLORS.ink,
          opacity: titleO,
          textAlign: "center",
        }}
      >
        Ship a RAG assistant your team can <span style={{ color: COLORS.orange }}>trust.</span>
      </div>
      <div
        style={{
          marginTop: 22,
          fontSize: 27,
          fontWeight: 600,
          color: COLORS.muted,
          opacity: titleO,
          letterSpacing: 0.5,
        }}
      >
        Self-hosted · Dockerized · every answer measured and sourced.
      </div>

      <div
        style={{
          marginTop: 46,
          background: COLORS.ink,
          color: "#eceff1",
          fontFamily: mono,
          fontSize: 27,
          padding: "20px 34px",
          borderRadius: 12,
          boxShadow: "0 20px 44px rgba(35,40,43,.28)",
          transform: `translateY(${cmdY}px)`,
          opacity: cmdO,
        }}
      >
        <span style={{ color: COLORS.slate }}>$</span> docker compose up{" "}
        <span style={{ color: COLORS.orange }}>--build</span>
      </div>

      <div
        style={{
          marginTop: 34,
          fontSize: 24,
          fontWeight: 700,
          letterSpacing: 3,
          color: COLORS.slate,
          opacity: urlO,
          fontFamily: mono,
        }}
      >
        → http://localhost:8000
      </div>
    </AbsoluteFill>
  );
};
