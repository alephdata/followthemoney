const withMarkdoc = require('@markdoc/next.js');

/** @type {import('next').NextConfig} */
// const nextConfig = {
//   reactStrictMode: true,
//   swcMinify: true,
//   trailingSlash: true,
// }

const markdocConfig = withMarkdoc()({
  pageExtensions: ['md', 'mdoc','js', 'jsx', 'ts', 'tsx'],
  reactStrictMode: true,
  swcMinify: true,
  trailingSlash: true,
});
// console.log(bla)

module.exports = markdocConfig;
