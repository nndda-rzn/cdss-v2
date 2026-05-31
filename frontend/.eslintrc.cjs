module.exports = {
  root: true,
  env: { browser: true, es2020: true },
  extends: [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:react-hooks/recommended",
  ],
  parser: "@typescript-eslint/parser",
  plugins: ["react-refresh"],
  rules: {
    "react-refresh/only-export-components": "warn",
    // File-size budget: keep components/modules focused. Split when exceeded.
    "max-lines": ["warn", { max: 200, skipBlankLines: true, skipComments: true }],
  },
  overrides: [
    {
      // Tests and generated shadcn primitives may legitimately run longer.
      files: ["**/*.test.{ts,tsx}", "src/components/ui/**"],
      rules: { "max-lines": "off" },
    },
  ],
};
