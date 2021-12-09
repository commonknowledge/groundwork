/** @type {import('ts-jest/dist/types').InitialOptionsTsJest} */
module.exports = {
  testEnvironment: "jsdom",
  moduleNameMapper: {
    "\\.(jpg|jpeg|png|gif|eot|otf|webp|svg|ttf|woff|woff2|mp4|webm|wav|mp3|m4a|aac|oga)$":
      require.resolve("./frontend/core/util/file-mock.ts"),
    "\\.(css|scss)$": require.resolve("./frontend/core/util/file-mock.ts"),
  },
  setupFiles: ["mutationobserver-shim"],
  testPathIgnorePatterns: ["/node_modules/", "<rootDir>/build/"],
};
