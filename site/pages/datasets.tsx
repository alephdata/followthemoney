import type { NextPage } from 'next'
import Head from 'next/head'
import Image from 'next/image'

import 'bootstrap/dist/css/bootstrap.css'
import styles from '../styles/Home.module.css'

const Datasets: NextPage = () => {
    return (
        <div className={styles.container}>
            <Head>
                <title>followthemoney.tech</title>
                <meta name="description" content="Details for the followthemoney data model" />
                <link rel="icon" href="/favicon.ico" />
            </Head>

            <main className={styles.main}>
                <h1 className={styles.title}>
                    dataset listing
                </h1>
            </main>

            <footer className={styles.footer}>
            </footer>
        </div>
    )
}

export default Datasets
