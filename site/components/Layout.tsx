import React from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';

import Navbar from './Navbar';
import Footer from './Footer';
import { BASE_URL, SITE } from '../lib/constants';

import styles from '../styles/Layout.module.scss';


type LayoutBaseProps = {
  title?: string,
  description?: string | null,
  imageUrl?: string | null
}

export default function Layout({ title, description, imageUrl, children }: React.PropsWithChildren<LayoutBaseProps>) {
  const router = useRouter();
  const url = `${BASE_URL}${router.asPath}`;
  const fullTitle = `${title}`
  return (
    <>
      <Head>
        {title && (
          <>
            <title>{fullTitle}</title>
            <meta property="og:title" content={title} />
            <meta property="twitter:title" content={title} />
          </>
        )}
        <link rel="apple-touch-icon" sizes="180x180" href="/static/apple-touch-icon.png" />
        <link rel="icon" type="image/png" sizes="32x32" href="/static/favicon-32x32.png" />
        <link rel="icon" type="image/png" sizes="16x16" href="/static/favicon-16x16.png" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="twitter:card" content="summary" />
        <meta name="twitter:site" content="@alephdata" />
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
        {children}
      </div>
      <Footer />
    </>
  )
}
