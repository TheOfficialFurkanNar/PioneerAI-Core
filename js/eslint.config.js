const { eslint } = require("@eslint/js");
const tsPlugin = require("@typescript-eslint/eslint-plugin");
const reactPlugin = require("eslint-plugin-react");
const importPlugin = require("eslint-plugin-import");
const prettierPlugin = require("eslint-plugin-prettier");

module.exports = [
  eslint.configs.recommended,
  {
    plugins: {
      "@typescript-eslint": tsPlugin,
      react: reactPlugin,
      import: importPlugin,
      prettier: prettierPlugin,
    },
    rules: {
      "no-unused-vars": "warn",
      "no-console": "off",
      "react/prop-types": "off",
      "import/order": [
        "warn",
        {
          groups: [["builtin", "external"], "internal", ["parent", "sibling", "index"]],
          "newlines-between": "always",
        },
      ],
    },
    languageOptions: {
      sourceType: "module",
      ecmaVersion: "latest",
    },
    settings: {
      react: {
        version: "detect",
      },
    },
  },
];