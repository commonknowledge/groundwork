import * as path from "path";
import { defineConfig } from "vite";
import legacy from "@vitejs/plugin-legacy";
import { useDynamicPublicPath } from "vite-plugin-dynamic-publicpath";

import { peerDependencies } from "./package.json";
import { resolve } from "path";

export default defineConfig(({ mode }) => {
  // Bundled mode:
  // - JS distributed via pypi. npm package and frontend js toolchain not required.
  // - All dependencies included in bundle.
  //
  // Unbundled mode:
  // - JS distributed via npm. Frontend widgets require this to be built.
  // - Some dependencies included in bundle.
  // - Some dependencies externalised (see package.json peerDependencies field)
  //
  // Test-utils mode:
  // - JS distributed via npm. Available via `import 'groundwork-ui/test-utils'`
  // - Some dependencies included in bundle.
  // - Some dependencies externalised (see package.json peerDependencies field)
  // - Some dependencies that will throw in test environments (such as mapbox) replaced with the mock we use internally
  //   for testing.

  const isBundled = mode === "bundled";
  const isDev = mode === "dev";

  const isTestUtils = mode === "test-utils";
  const isLibrary = !isBundled && !isDev;

  const entrypoint = `frontend/index.${mode}.ts`;
  const outDir = isBundled ? "pyck/core/static/groundwork/" : `build/${mode}/`;

  const alias = !isTestUtils
    ? []
    : TEST_MOCKS.map((moduleName) => ({
        find: new RegExp(`^${moduleName}$`),
        replacement: resolve(`__mocks__/${moduleName}.ts`),
      }));

  return {
    // In bundled mode, we use the dynamicPublicPath plugin instead of a hardcoded asset path
    base: isBundled ? "" : "/static/",
    optimizeDeps: {
      entries: [entrypoint],
    },
    plugins: compact([
      isBundled &&
        legacy({
          polyfills: false,
          targets: ["defaults", "not IE 11"],
        }),
      isBundled &&
        // In bundled mode, we need to inject STATIC_URL into templates and pick it up with these
        useDynamicPublicPath({
          dynamicImportHandler: "window.__groundwork_dynamic_handler__",
          dynamicImportPreload: "window.__groundwork_dynamic_preload__",
        }),
    ]),
    resolve: {
      alias,
    },
    build: {
      manifest: isBundled,
      emptyOutDir: true,
      outDir,
      rollupOptions: {
        external: isBundled ? [] : Object.keys(peerDependencies),
        output: {
          dir: outDir,
        },

        input: {
          main: entrypoint,
        },
      },
      lib: !isLibrary
        ? undefined
        : {
            entry: path.resolve(__dirname, entrypoint),
            formats: isBundled ? ["cjs"] : ["es"],
            name: "groundwork",
            fileName: () => `index.js`,
          },
    },
  };
});

const TEST_MOCKS = ["mapbox-gl"];

const compact = (array) => array.filter((item) => !!item);
