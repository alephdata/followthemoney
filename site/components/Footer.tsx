import React from 'react';
import Link from 'next/link';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';

import styles from '../styles/Footer.module.scss';

import Nav from "react-bootstrap/Nav";
import Navbar from "react-bootstrap/Navbar";
import Container from 'react-bootstrap/Container';

export default class Footer extends React.Component {
  render() {
    return (
      <Navbar bg="light" variant="light" fixed="bottom">
        <Container>
          <span className="text-muted">Copyright 2022</span>
        </Container>
      </Navbar>
    )
  }
}