import eslint from '@eslint/js';
import tseslint from 'typescript-eslint';

export default tseslint.config({
  files: ["src/**/*.ts"],
  ignores: ["rollup.config.mjs", "coverage/**"],
  extends: [
    eslint.configs.recommended,
    ...tseslint.configs.recommended,
  ]
});