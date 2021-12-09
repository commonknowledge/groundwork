const { ExtractorConfig, Extractor } = require("@microsoft/api-extractor");

const IGNORED_SYMBOLS = ["mapbox-gl"];

/**
 * Rollup the d.ts files produced by typescript into single files to go with the rolled-up library.
 */
const invoke = (slug) => {
  const packageJson = require("../package.json");
  const peerDependencies = new Set([
    ...Object.keys(packageJson.peerDependencies),
    ...IGNORED_SYMBOLS,
  ]);

  const config = ExtractorConfig.prepare({
    configObject: {
      mainEntryPointFilePath: `<projectFolder>/build/ts/frontend/index.${slug}.d.ts`,
      bundledPackages: [
        ...Object.keys(packageJson.dependencies ?? {}),
        ...Object.keys(packageJson.devDependencies).filter(
          (x) => !peerDependencies.has(x)
        ),
      ],
      projectFolder: process.cwd(),
      compiler: {
        tsconfigFilePath: "<projectFolder>/tsconfig.json",
      },
      dtsRollup: {
        enabled: true,
        publicTrimmedFilePath: `<projectFolder>/build/${slug}/index.d.ts`,
      },
      apiReport: {
        enabled: false,
        reportFileName: "<unscopedPackageName>.api.md",
      },
      docModel: {
        enabled: false,
      },
      tsdocMetadata: {
        enabled: false,
      },
    },
    configObjectFullPath: undefined,
    packageJson,
    packageJsonFullPath: require.resolve("../package.json"),
  });

  Extractor.invoke(config, {
    localBuild: true,
    showVerboseMessages: true,
  });
};

// import * from 'groundwork-ui/test-utils'
invoke("test-utils");

// import * from 'groundwork-ui'
invoke("lib");
