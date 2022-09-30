import Document, { Html, Head, Main, NextScript } from 'next/document';

export default class SiteDocument extends Document {
  render() {
    return (
      <Html lang="en">
        <Head />
        <body>
          <Main />
          <NextScript />
        </body>
      </Html>
    )
  }
}