const { eslint } = require("@eslint/js");
const tsPlugin = require("@typescript-eslint/eslint-plugin");
const reactPlugin = require("eslint-plugin-react");
const importPlugin = require("eslint-plugin-import");
const prettierPlugin = require("eslint-plugin-prettier");
const reactHooksPlugin = require("eslint-plugin-react-hooks"); // Import React Hooks plugin

module.exports = [
  eslint.configs.recommended,
  {
    plugins: {
      "@typescript-eslint": tsPlugin,
      react: reactPlugin,
      import: importPlugin,
      prettier: prettierPlugin,
      "react-hooks": reactHooksPlugin, // Add React Hooks plugin
    },
    rules: {
      // General JS/TS rules
      "no-unused-vars": "warn",
      "no-console": process.env.NODE_ENV === "production" ? "warn" : "off",

      // React rules
      "react/prop-types": "off",
      "react/jsx-uses-react": "off", // Not needed in React 17+
      "react/react-in-jsx-scope": "off", // Not needed in React 17+

      // Import rules
      "import/order": [
        "warn",
        {
          groups: [
            ["builtin", "external"],
            "internal",
            ["parent", "sibling", "index"]
          ],
          "newlines-between": "always",
          alphabetize: { order: "asc", caseInsensitive: true }
        }
      ],

      // Prettier integration
      "prettier/prettier": [
        "warn",
        {
          singleQuote: true,
          trailingComma: "all",
          printWidth: 100,
          tabWidth: 2,
          semi: true,
        }
      ],

      // TypeScript rules
      "@typescript-eslint/explicit-function-return-type": "warn",
      "@typescript-eslint/no-explicit-any": "warn",
      "@typescript-eslint/no-unused-vars": "warn",
      "@typescript-eslint/no-unused-expressions": "warn",

      // React Hooks rules
      "react-hooks/rules-of-hooks": "error", // Checks rules of Hooks
      "react-hooks/exhaustive-deps": "warn", // Checks effect dependencies
    },
    languageOptions: {
      sourceType: "module",
      ecmaVersion: "latest",
    },
    settings: {
      react: {
        version: "detect",
      },
      "import/resolver": {
        node: {
          extensions: [".js", ".jsx", ".ts", ".tsx", ".json"]
        }
      },
    },
  },
];