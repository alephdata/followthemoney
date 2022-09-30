const withMarkdoc = require('@markdoc/next.js');

/** @type {import('next').NextConfig} */
// const nextConfig = {
//   reactStrictMode: true,
//   swcMinify: true,
//   trailingSlash: true,
// }

const bla = withMarkdoc()({
  pageExtensions: ['md', 'mdoc'],
  reactStrictMode: true,
  swcMinify: true,
  trailingSlash: true,
});
// console.log(bla)

module.exports = bla;
