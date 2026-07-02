import { Composition } from "remotion";
import { TrinityPromo } from "./TrinityPromo";
import { FPS, HEIGHT, TOTAL, WIDTH } from "./theme";

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="TrinityPromo"
      component={TrinityPromo}
      durationInFrames={TOTAL}
      fps={FPS}
      width={WIDTH}
      height={HEIGHT}
    />
  );
};
