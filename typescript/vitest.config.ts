// The reducer and the codec, against the golden fixture. No network, no keys.
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    include: ["test/**/*.test.ts"],
  },
});
