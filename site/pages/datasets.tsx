import type { NextPage } from 'next'
import Head from 'next/head'
import Image from 'next/image'

import 'bootstrap/dist/css/bootstrap.css'
import styles from '../styles/Home.module.scss'
import Layout from '../components/Layout'

const Datasets: NextPage = () => {
  return (
    <main className={styles.main}>
      <h1 className={styles.title}>
        dataset listing
      </h1>
    </main>
  )
}

export default Datasets
