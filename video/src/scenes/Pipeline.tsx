import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { COLORS } from "../theme";
import { fadeInOut, pop, reveal } from "../helpers";

type Node = { icon: string; label: string; accent?: boolean };

const INDEX_NODES: Node[] = [
  { icon: "📄", label: "PDFs" },
  { icon: "✂️", label: "Parse & chunk" },
  { icon: "🔢", label: "Embed" },
  { icon: "🗄️", label: "ChromaDB", accent: true },
];

const ASK_NODES: Node[] = [
  { icon: "💬", label: "Question" },
  { icon: "🔎", label: "Vector search" },
  { icon: "🧩", label: "Augment" },
  { icon: "🤖", label: "LLM" },
  { icon: "✅", label: "Answer", accent: true },
];

const NodePill: React.FC<{
  node: Node;
  index: number;
  startFrame: number;
  frame: number;
  fps: number;
}> = ({ node, index, startFrame, frame, fps }) => {
  const delay = startFrame + index * 9;
  const s = pop(frame, fps, delay);
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 12,
        width: 190,
        transform: `scale(${s})`,
        opacity: s,
      }}
    >
      <div
        style={{
          width: 108,
          height: 108,
          borderRadius: 22,
          background: node.accent ? COLORS.orange : "#fff",
          border: `2px solid ${node.accent ? COLORS.orange : COLORS.panelBorder}`,
          boxShadow: node.accent
            ? "0 16px 34px rgba(190,77,0,.28)"
            : "0 12px 26px rgba(35,40,43,.08)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: 50,
        }}
      >
        {node.icon}
      </div>
      <div
        style={{
          fontSize: 23,
          fontWeight: 700,
          color: node.accent ? COLORS.orange : COLORS.ink,
          textAlign: "center",
        }}
      >
        {node.label}
      </div>
    </div>
  );
};

const Connector: React.FC<{
  index: number;
  startFrame: number;
  frame: number;
}> = ({ index, startFrame, frame }) => {
  const start = startFrame + index * 9 + 5;
  const fill = reveal(frame, start, start + 8);
  return (
    <div
      style={{
        width: 70,
        height: 4,
        background: COLORS.line,
        borderRadius: 3,
        position: "relative",
        marginBottom: 40,
      }}
    >
      <div
        style={{
          position: "absolute",
          left: 0,
          top: 0,
          height: "100%",
          width: `${fill * 100}%`,
          background: COLORS.slate,
          borderRadius: 3,
        }}
      />
    </div>
  );
};

const Flow: React.FC<{
  title: string;
  nodes: Node[];
  startFrame: number;
  frame: number;
  fps: number;
}> = ({ title, nodes, startFrame, frame, fps }) => {
  const titleO = reveal(frame, startFrame - 4, startFrame + 8);
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
      <div
        style={{
          fontSize: 18,
          fontWeight: 700,
          letterSpacing: 4,
          color: COLORS.slate,
          opacity: titleO,
          marginBottom: 14,
        }}
      >
        {title}
      </div>
      <div style={{ display: "flex", alignItems: "center" }}>
        {nodes.map((n, i) => (
          <div key={n.label} style={{ display: "flex", alignItems: "center" }}>
            <NodePill
              node={n}
              index={i}
              startFrame={startFrame}
              frame={frame}
              fps={fps}
            />
            {i < nodes.length - 1 && (
              <Connector index={i} startFrame={startFrame} frame={frame} />
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export const Pipeline: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const opacity = fadeInOut(frame, durationInFrames, 10, 16);
  const headO = reveal(frame, 2, 18);
  const headY = interpolate(headO, [0, 1], [18, 0]);

  return (
    <AbsoluteFill
      style={{
        opacity,
        background: "#fbfcfc",
        alignItems: "center",
        justifyContent: "center",
        gap: 70,
      }}
    >
      <div
        style={{
          position: "absolute",
          top: 90,
          fontSize: 52,
          fontWeight: 700,
          color: COLORS.ink,
          opacity: headO,
          transform: `translateY(${headY}px)`,
        }}
      >
        How <span style={{ color: COLORS.slate }}>Ask Trinity</span> works
      </div>

      <Flow
        title="INDEX  ·  ONCE"
        nodes={INDEX_NODES}
        startFrame={24}
        frame={frame}
        fps={fps}
      />
      <Flow
        title="ASK  ·  EVERY QUESTION"
        nodes={ASK_NODES}
        startFrame={92}
        frame={frame}
        fps={fps}
      />
    </AbsoluteFill>
  );
};
