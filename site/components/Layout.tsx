import React from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';

import Navbar from './Navbar';
import Footer from './Footer';
import { BASE_URL, SITE } from '../lib/constants';

import styles from '../styles/Layout.module.scss';

import type { AppProps } from 'next/app'
import type { MarkdocNextJsPageProps } from '@markdoc/next.js'

export type MyAppProps = MarkdocNextJsPageProps

type LayoutBaseProps = {
  title?: string,
  description?: string | null,
  imageUrl?: string | null
}

const GetLayout = ({Component, pageProps}) => {
  if(Component.getLayout) {
    return Component.getLayout(<Component {...pageProps} />)
  } else {
    return <Component {...pageProps} />
  }  
}

export default function Layout({ Component, pageProps }: AppProps<MyAppProps>) {
  const { markdoc } = pageProps;
  const DEFAULT_TITLE = "";
  const DEFAULT_DESCRIPTION = "";
  const DEFAULT_IMAGE_URL = "";
  const url = "#";

  const title = markdoc && markdoc.frontmatter.title || DEFAULT_TITLE;
  const description = markdoc && markdoc.frontmatter.description || DEFAULT_DESCRIPTION;
  const imageUrl = markdoc && markdoc.frontmatter.imageUrl || DEFAULT_IMAGE_URL;

  return (
    <>
      <Head>
        {title && (
          <>
            <title>{title}</title>
            <meta property="og:title" content={title} />
            <meta property="twitter:title" content={title} />
          </>
        )}
        {!!description && (
          <>
            <meta property="og:description" content={description.trim()} />
            <meta name="description" content={description.trim()} />
          </>
        )}
        {imageUrl && (
          <meta property="og:image" content={imageUrl} />
        )}
        <meta name="og:site" content={SITE} />
        <meta property="og:url" content={url} />
      </Head>
      <div className={styles.page}>
        <Navbar />
        <GetLayout Component={Component} pageProps={pageProps} />
      </div>
      <Footer />
    </>
  )
}
