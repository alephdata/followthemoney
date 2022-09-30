/** @type {import('next').NextConfig} */
const withMarkdoc = require('@markdoc/next.js');

const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  trailingSlash: true,
}

module.exports = withMarkdoc(nextConfig)({
  pageExtensions: ['md', 'mdoc', 'js', 'jsx', 'ts', 'tsx']
});
