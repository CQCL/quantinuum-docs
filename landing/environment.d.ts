import { runtimeENVs } from "./next.config.mjs";
import { z } from "zod";

declare global {
  namespace NodeJS {
    interface ProcessEnv extends z.infer<typeof runtimeENVs> {}
  }
}
