const { ExtractorConfig, Extractor } = require("@microsoft/api-extractor");

const IGNORED_SYMBOLS = ["mapbox-gl"];

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

invoke("test-utils");
invoke("lib");
