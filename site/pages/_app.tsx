import type { AppProps } from 'next/app'

import '../styles/globals.scss';
import Layout from '../components/Layout';

const Test = ({Component, pageProps}) => {
  if(Component.getLayout) {
    return Component.getLayout(<Component {...pageProps} />)
  } else {
    return <Component {...pageProps} />
  }  
}

function FollowTheMoneyApp({ Component, pageProps }: AppProps) {
  return(
    <Layout Component={Component} pageProps={pageProps}>
      <Test Component={Component} pageProps={pageProps} />
    </Layout>
  );
}

export default FollowTheMoneyApp
