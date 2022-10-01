import type { AppProps } from 'next/app'

import '../styles/globals.scss';
import Layout from '../components/Layout';

function FollowTheMoneyApp({ Component, pageProps }: AppProps) {
  return(
    <Layout Component={Component} pageProps={pageProps} />
  );
}

export default FollowTheMoneyApp
