import type { AppContext, AppInitialProps, AppLayoutProps, AppProps } from 'next/app'
import type { NextComponentType } from 'next';

import Layout from '../components/Layout';

import '../styles/globals.scss';

const FollowTheMoneyApp: NextComponentType<AppContext, AppInitialProps, AppLayoutProps> = ({
  Component,
  pageProps,
  router
}: AppLayoutProps) => {
  return(
    <Layout
      Component={Component}
      pageProps={pageProps}
      router={router}
    />
  );
}

export default FollowTheMoneyApp
