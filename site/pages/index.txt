import type { NextPage } from 'next'
import Head from 'next/head'
import Image from 'next/image'

import Layout from '../components/Layout'
import styles from '../styles/Home.module.scss'

const Home: NextPage = () => {
  return (
    <Layout title="Follow the Money" description="Documentation for the anti-corruption data stack">
      <main className={styles.main}>
        <h1 className={styles.title}>
          FollowTheMoney web site
        </h1>
      </main>
    </Layout>
  )
}

export default Home
