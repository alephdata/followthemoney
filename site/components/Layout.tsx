import React from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';

import TopNav from './TopNav';
import Footer from './Footer';
import Sidebar from './Sidebar';

import { BASE_URL, SITE } from '../lib/constants';

import styles from '../styles/Layout.module.scss';

import type { AppProps } from 'next/app'
import type { MarkdocNextJsPageProps } from '@markdoc/next.js'

import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';


export type MyAppProps = MarkdocNextJsPageProps

const GetLayout = ({Component, pageProps}) => {
  if(Component.getLayout) {
    return Component.getLayout(<Component {...pageProps} />)
  } else {
    return <Component {...pageProps} />
  }  
}

const collectHeadings = (node, sections = []) => {
  if (node && node.name) {
    if (node.name.match(/h\d/)) {
      const title = node.children[0];

      if (typeof title === 'string') {
        sections.push({
          ...node.attributes,
          title
        });
      }
    }

    if (node.children) {
      for (const child of node.children) {
        collectHeadings(child, sections);
      }
    }
  }

  return sections;
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

  const toc = markdoc.content ? collectHeadings(markdoc.content) : [];

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
      <Container fluid className="h-100">
        <Row>
          <TopNav />
        </Row>
        <Row className="h-100">
          <Col xs={2}>
            <Sidebar headings={toc}></Sidebar>
          </Col>
          <Col xs={6}>
            <GetLayout Component={Component} pageProps={pageProps} />
          </Col>
        </Row>
        <Row><Footer /></Row>
      </Container>
    </>
  )
}
