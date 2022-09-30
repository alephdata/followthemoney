import React from 'react';
import Link from 'next/link';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Container from 'react-bootstrap/Container';

import styles from '../styles/Footer.module.scss';

export default class Footer extends React.Component {
  render() {
    return (
      <div className={styles.footer}>
        <Container>
          <Row>
            <Col>

            </Col>
          </Row>
        </Container >
      </div >
    )
  }
}