import { AbsoluteFill, Sequence } from "remotion";
import { loadFont } from "@remotion/google-fonts/TitilliumWeb";
import { COLORS, SCENE } from "./theme";
import { Intro } from "./scenes/Intro";
import { Problem } from "./scenes/Problem";
import { Pipeline } from "./scenes/Pipeline";
import { Features } from "./scenes/Features";
import { CTA } from "./scenes/CTA";

const { fontFamily } = loadFont();

export const TrinityPromo: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.paper, fontFamily }}>
      <Sequence from={SCENE.intro.from} durationInFrames={SCENE.intro.duration}>
        <Intro />
      </Sequence>
      <Sequence
        from={SCENE.problem.from}
        durationInFrames={SCENE.problem.duration}
      >
        <Problem />
      </Sequence>
      <Sequence
        from={SCENE.pipeline.from}
        durationInFrames={SCENE.pipeline.duration}
      >
        <Pipeline />
      </Sequence>
      <Sequence
        from={SCENE.features.from}
        durationInFrames={SCENE.features.duration}
      >
        <Features />
      </Sequence>
      <Sequence from={SCENE.cta.from} durationInFrames={SCENE.cta.duration}>
        <CTA />
      </Sequence>
    </AbsoluteFill>
  );
};
