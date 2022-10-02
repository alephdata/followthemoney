import type { AppProps } from 'next/app'
import Layout from '../components/Layout';

import '../styles/globals.scss';

function FollowTheMoneyApp({ Component, pageProps }: AppProps) {
  return(
    <Layout Component={Component} pageProps={pageProps} />
  );
}

export default FollowTheMoneyApp
