import type { AppProps } from 'next/app'

import '../styles/globals.scss'

function FollowTheMoneyApp({ Component, pageProps }: AppProps) {
  return <Component {...pageProps} />
}

export default FollowTheMoneyApp
