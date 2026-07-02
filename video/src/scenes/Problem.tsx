import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { COLORS } from "../theme";
import { fadeInOut, pop, reveal } from "../helpers";

const DOCS = [
  "tank-cars.pdf",
  "covered-hoppers.pdf",
  "leasing.pdf",
  "rail-shipping.pdf",
  "fuel-surcharge.pdf",
  "logistics.pdf",
  "gondolas.pdf",
  "boxcars.pdf",
];

const PdfCard: React.FC<{ label: string; i: number; frame: number; fps: number }> = ({
  label,
  i,
  frame,
  fps,
}) => {
  const s = pop(frame, fps, 6 + i * 3);
  const angle = (i - DOCS.length / 2) * 5;
  const x = (i - DOCS.length / 2) * 118;
  const y = Math.abs(i - DOCS.length / 2) * 14;
  return (
    <div
      style={{
        position: "absolute",
        width: 150,
        height: 194,
        borderRadius: 12,
        background: "#fff",
        border: `1px solid ${COLORS.panelBorder}`,
        boxShadow: "0 20px 40px rgba(35,40,43,.10)",
        transform: `translate(${x}px, ${y}px) rotate(${angle}deg) scale(${s})`,
        opacity: s,
        padding: 16,
        display: "flex",
        flexDirection: "column",
        gap: 9,
      }}
    >
      <div
        style={{
          width: 40,
          height: 18,
          borderRadius: 4,
          background: COLORS.orange,
          color: "#fff",
          fontSize: 11,
          fontWeight: 700,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          letterSpacing: 1,
        }}
      >
        PDF
      </div>
      {[0.95, 0.7, 0.85, 0.55, 0.8, 0.4].map((w, k) => (
        <div
          key={k}
          style={{
            height: 8,
            width: `${w * 100}%`,
            borderRadius: 3,
            background: COLORS.line,
          }}
        />
      ))}
      <div
        style={{
          marginTop: "auto",
          fontSize: 10,
          color: COLORS.muted,
          fontWeight: 600,
          overflow: "hidden",
          textOverflow: "ellipsis",
          whiteSpace: "nowrap",
        }}
      >
        {label}
      </div>
    </div>
  );
};

export const Problem: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const opacity = fadeInOut(frame, durationInFrames, 10, 14);
  const headO = reveal(frame, 4, 22);
  const headY = interpolate(headO, [0, 1], [20, 0]);
  const subO = reveal(frame, 40, 58);

  return (
    <AbsoluteFill
      style={{
        opacity,
        background: "#fbfcfc",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <div
        style={{
          fontSize: 62,
          fontWeight: 700,
          color: COLORS.ink,
          textAlign: "center",
          transform: `translateY(${headY}px)`,
          opacity: headO,
          maxWidth: 1200,
          lineHeight: 1.1,
        }}
      >
        Your product knowledge is{" "}
        <span style={{ color: COLORS.orange }}>trapped in PDFs.</span>
      </div>

      <div
        style={{
          position: "relative",
          width: 1200,
          height: 300,
          marginTop: 70,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        {DOCS.map((d, i) => (
          <PdfCard key={d} label={d} i={i} frame={frame} fps={fps} />
        ))}
      </div>

      <div
        style={{
          fontSize: 28,
          fontWeight: 600,
          color: COLORS.muted,
          opacity: subO,
          marginTop: 40,
          letterSpacing: 0.5,
        }}
      >
        Specs, leasing terms, logistics — scattered across dozens of documents.
      </div>
    </AbsoluteFill>
  );
};
