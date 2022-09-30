import 'bootstrap/dist/css/bootstrap.css'
import '../styles/globals.css'

import type { AppProps } from 'next/app'

function FollowTheMoneyApp({ Component, pageProps }: AppProps) {
  return <Component {...pageProps} />
}

export default FollowTheMoneyApp
