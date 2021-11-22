import * as path from "path";
import { defineConfig } from "vite";
import legacy from "@vitejs/plugin-legacy";
import tsconfigPaths from "vite-tsconfig-paths";

import { peerDependencies } from "./package.json";

export default defineConfig(({ mode }) => {
  // Bundled mode:
  // - JS distributed via pypi. npm package and frontend js toolchain not required.
  // - All dependencies included in bundle.
  //
  // Unbundled mode:
  // - JS distributed via npm. Frontend widgets require this to be built.
  // - Some dependencies included in bundle.
  // - Some dependencies externalised (see package.json peerDependencies field)

  const isBundled = mode === "bundled";
  const isDev = mode === "dev";
  const entrypoint = isBundled ? "register.ts" : "index.ts";

  return {
    base: "/static/",
    optimizeDeps: {
      entries: ["./pyck/core/frontend/index.ts"],
    },
    plugins: compact([
      tsconfigPaths(),
      isBundled &&
        legacy({
          polyfills: false,
          targets: ["defaults", "not IE 11"],
        }),
    ]),
    build: {
      emptyOutDir: true,
      rollupOptions: {
        external: isBundled ? [] : Object.keys(peerDependencies),
        output: {
          dir: isBundled ? "pyck/core/static/" : "dist/",
        },
        input: {
          main: `pyck/core/frontend/${entrypoint}`,
        },
      },
      lib:
        isBundled || isDev
          ? undefined
          : {
              entry: path.resolve(
                __dirname,
                `pyck/core/frontend/${entrypoint}`
              ),
              formats: isBundled ? ["cjs"] : ["es"],
              name: "pyck",
              fileName: () => `index.js`,
            },
    },
  };
});

const compact = (array) => array.filter((item) => !!item);
