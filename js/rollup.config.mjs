import resolve from '@rollup/plugin-node-resolve';
import nodeResolve from '@rollup/plugin-node-resolve';
import commonjs from '@rollup/plugin-commonjs';
import typescript from '@rollup/plugin-typescript';
import json from '@rollup/plugin-json';
import pkg from './package.json' with {type: 'json'};

const libraryName = 'followthemoney'

export default {
  input: `src/index.ts`,
  output: [
    { file: pkg.main, name: libraryName, format: 'umd', sourcemap: true, globals: { crypto: 'crypto' } },
    { file: pkg.module, format: 'es', sourcemap: true, globals: { crypto: 'crypto' } },
  ],
  // Indicate here external modules you don't wanna include in your bundle (i.e.: 'lodash')
  external: ['crypto'],
  watch: {
    include: 'src/**',
  },
  plugins: [
    // Allow json resolution
    json(),
    nodeResolve({
      preferBuiltins: true
    }),
    // Allow node_modules resolution, so you can use 'external' to control
    // which external modules to include in the bundle
    // https://github.com/rollup/rollup-plugin-node-resolve#usage
    resolve({ browser: true }),
    // Compile TypeScript files
    typescript({ sourceMap: true, inlineSources: true }),
    // Allow bundling cjs modules (unlike webpack, rollup doesn't understand cjs)
    commonjs(),
  ],
}
