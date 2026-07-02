import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { COLORS } from "../theme";
import { fadeInOut, pop, reveal } from "../helpers";

const mono = "ui-monospace, Menlo, monospace";

const Card: React.FC<{
  delay: number;
  frame: number;
  fps: number;
  style?: React.CSSProperties;
  children: React.ReactNode;
}> = ({ delay, frame, fps, style, children }) => {
  const s = pop(frame, fps, delay);
  const y = interpolate(s, [0, 1], [40, 0]);
  return (
    <div
      style={{
        background: "#fff",
        borderRadius: 18,
        border: `1px solid ${COLORS.panelBorder}`,
        boxShadow: "0 24px 50px rgba(35,40,43,.10)",
        transform: `translateY(${y}px)`,
        opacity: s,
        padding: 30,
        ...style,
      }}
    >
      {children}
    </div>
  );
};

const SimilarityRow: React.FC<{
  name: string;
  pct: number;
  frame: number;
  start: number;
}> = ({ name, pct, frame, start }) => {
  const fill = reveal(frame, start, start + 16) * pct;
  return (
    <div style={{ marginBottom: 16 }}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          fontSize: 18,
          color: COLORS.ink,
          marginBottom: 7,
          fontFamily: mono,
        }}
      >
        <span style={{ color: COLORS.muted }}>{name}</span>
        <span style={{ color: COLORS.slate, fontWeight: 700 }}>
          {(fill * 100).toFixed(1)}%
        </span>
      </div>
      <div
        style={{
          height: 9,
          background: COLORS.line,
          borderRadius: 5,
          overflow: "hidden",
        }}
      >
        <div
          style={{
            width: `${fill * 100}%`,
            height: "100%",
            background: COLORS.slate,
            borderRadius: 5,
          }}
        />
      </div>
    </div>
  );
};

const MetricBar: React.FC<{
  label: string;
  ms: number;
  max: number;
  frame: number;
  start: number;
}> = ({ label, ms, max, frame, start }) => {
  const t = reveal(frame, start, start + 20);
  const shown = Math.round(t * ms);
  return (
    <div style={{ marginBottom: 20 }}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          fontSize: 19,
          marginBottom: 8,
          fontFamily: mono,
        }}
      >
        <span style={{ color: COLORS.ink, fontWeight: 700 }}>{label}</span>
        <span style={{ color: COLORS.orange, fontWeight: 700 }}>{shown} ms</span>
      </div>
      <div
        style={{
          height: 12,
          background: COLORS.line,
          borderRadius: 6,
          overflow: "hidden",
        }}
      >
        <div
          style={{
            width: `${(t * ms * 100) / max}%`,
            height: "100%",
            background: `linear-gradient(90deg, ${COLORS.orange}, ${COLORS.orangeDark})`,
            borderRadius: 6,
          }}
        />
      </div>
    </div>
  );
};

export const Features: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const opacity = fadeInOut(frame, durationInFrames, 10, 16);
  const headO = reveal(frame, 2, 18);
  const headY = interpolate(headO, [0, 1], [18, 0]);
  const tokens = Math.round(reveal(frame, 70, 100) * 1480);

  return (
    <AbsoluteFill
      style={{
        opacity,
        background: "linear-gradient(180deg, #ffffff 0%, #f1f4f5 100%)",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <div
        style={{
          position: "absolute",
          top: 78,
          fontSize: 52,
          fontWeight: 700,
          color: COLORS.ink,
          opacity: headO,
          transform: `translateY(${headY}px)`,
          textAlign: "center",
        }}
      >
        Grounded answers — <span style={{ color: COLORS.orange }}>with the receipts.</span>
      </div>

      <div style={{ display: "flex", gap: 34, marginTop: 60 }}>
        {/* Answer + sources */}
        <Card delay={10} frame={frame} fps={fps} style={{ width: 640 }}>
          <div
            style={{
              fontSize: 15,
              fontWeight: 700,
              letterSpacing: 3,
              color: COLORS.muted,
              marginBottom: 16,
            }}
          >
            ANSWER
          </div>
          <div style={{ fontSize: 22, lineHeight: 1.5, color: COLORS.ink }}>
            TrinityRail offers a broad tank car lineup — including{" "}
            <b style={{ color: COLORS.ink }}>general service</b>, pressure,
            and specialty cars for products like{" "}
            <b>anhydrous ammonia</b>, sulfuric acid, and asphalt.
          </div>
          <div
            style={{
              marginTop: 26,
              fontSize: 15,
              fontWeight: 700,
              letterSpacing: 3,
              color: COLORS.muted,
              marginBottom: 16,
            }}
          >
            RETRIEVED SOURCES · COSINE SIMILARITY
          </div>
          <SimilarityRow
            name="tank-cars.pdf"
            pct={0.912}
            frame={frame}
            start={40}
          />
          <SimilarityRow
            name="33560-gallon-pressure-tank-car.pdf"
            pct={0.871}
            frame={frame}
            start={48}
          />
          <SimilarityRow
            name="anhydrous-ammonia-tank-car.pdf"
            pct={0.844}
            frame={frame}
            start={56}
          />
        </Card>

        {/* Performance panel */}
        <Card delay={22} frame={frame} fps={fps} style={{ width: 560 }}>
          <div
            style={{
              fontSize: 15,
              fontWeight: 700,
              letterSpacing: 3,
              color: COLORS.muted,
              marginBottom: 24,
            }}
          >
            RAG PIPELINE PERFORMANCE
          </div>
          <MetricBar label="Embed" ms={18} max={860} frame={frame} start={50} />
          <MetricBar label="Search" ms={24} max={860} frame={frame} start={58} />
          <MetricBar
            label="Generate"
            ms={812}
            max={860}
            frame={frame}
            start={66}
          />
          <div
            style={{
              marginTop: 20,
              paddingTop: 22,
              borderTop: `1px solid ${COLORS.line}`,
              display: "flex",
              justifyContent: "space-between",
              alignItems: "flex-end",
            }}
          >
            <div>
              <div style={{ fontSize: 15, color: COLORS.muted, fontFamily: mono }}>
                TOKENS
              </div>
              <div
                style={{
                  fontSize: 40,
                  fontWeight: 700,
                  color: COLORS.ink,
                  fontFamily: mono,
                }}
              >
                {tokens.toLocaleString()}
              </div>
            </div>
            <div style={{ textAlign: "right" }}>
              <div style={{ fontSize: 15, color: COLORS.muted, fontFamily: mono }}>
                TOP_K · MODEL
              </div>
              <div
                style={{
                  fontSize: 22,
                  fontWeight: 700,
                  color: COLORS.slate,
                  fontFamily: mono,
                }}
              >
                8 · gpt-4o-mini
              </div>
            </div>
          </div>
        </Card>
      </div>

      <div
        style={{
          marginTop: 44,
          fontSize: 25,
          fontWeight: 600,
          color: COLORS.muted,
          opacity: reveal(frame, 96, 116),
        }}
      >
        Tune retrieval live in <span style={{ fontFamily: mono, color: COLORS.orange }}>config.py</span> · re-run · compare.
      </div>
    </AbsoluteFill>
  );
};
