const withMarkdoc = require('@markdoc/next.js');

/** @type {import('next').NextConfig} */

const markdocConfig = withMarkdoc()({
  pageExtensions: ['md', 'mdoc','js', 'jsx', 'ts', 'tsx'],
  reactStrictMode: true,
  swcMinify: true,
  trailingSlash: true,
});


module.exports = markdocConfig;
