import {
  Application,
  Controller,
  ControllerConstructor,
} from "@hotwired/stimulus";
import StimulusControllerResolver from "stimulus-controller-resolver";

/**
 * Convenience for:
 * - Starting a Stimulus app
 * - Registering async loaders for Stimulus controller modules
 * - Adding in loaders for all the controllers in this package.
 **/
export function startApp(...modules: AsyncModuleMap[]) {
  const app = Application.start();
  const allModules: AsyncModuleMap = Object.assign(
    {},
    EXPORTED_MODULES,
    ...modules
  );

  const resolver = createAsyncControllerResolver(allModules);

  StimulusControllerResolver.install(app, resolver);
  return app;
}

/**
 * Given a module map, return a function that returns the module constructor for an identifier.
 **/
const createAsyncControllerResolver = (pathMap: AsyncModuleMap) => {
  // Replace file paths in the module map with the controller identifier
  const identifierMap: AsyncModuleMap = Object.fromEntries(
    Object.entries(pathMap).flatMap(([path, loader]) => {
      const identifier = getIdentifierFromPath(path);
      if (identifier) {
        return [[identifier, loader]];
      }

      return [];
    })
  );

  return async (key: string) => {
    const module = await identifierMap[key]?.();
    if (!module) {
      throw Error(
        `Controller not found: ${key}. Have you named the file ${key}-controller.ts?`
      );
    }

    if (!module.default || !(module.default.prototype instanceof Controller)) {
      throw Error(
        `Module ${key} should have as its default export a subclass of Controller`
      );
    }

    return module.default;
  };
};

/**
 * Compiled-in references to all controllers in this package
 * See: https://vitejs.dev/guide/features.html#glob-import
 */
const EXPORTED_MODULES = import.meta.glob("../**/*-controller.ts");

/**
 * Given a path to a controller following the Stimulus file naming convention,
 * return its identifier
 **/
const getIdentifierFromPath = (fullPath: string) =>
  /([a-zA-Z-_0-9]*)[-_]controller\.(t|j)sx?$/.exec(fullPath)?.[1];

/**
 * Mapping of controller identifiers to async loaders for modules exporting a controller.
 */
interface AsyncModuleMap {
  [identifier: string]: () => Promise<{ default?: ControllerConstructor }>;
}
