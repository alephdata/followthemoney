import React from 'react';

import Container from 'react-bootstrap/Container';
import Nav from "react-bootstrap/Nav";
import Navbar from "react-bootstrap/Navbar";
import Link from 'next/link';
import NavLinks from './NavLinks';
import styles from '../styles/TopNav.module.scss';

export default class TopNav extends React.Component {
  render() {
    return (
      <Navbar bg="dark" variant="dark">
        <Container fluid>
          <Navbar.Brand href="/">FtM</Navbar.Brand>
          <Navbar.Collapse>
            <Nav className="main-nav">
              <Link href="/"><a className="nav-link">Home</a></Link>
              <Link href="/docs/introduction"><a className="nav-link">Docs</a></Link>
              <Link href="/model"><a className="nav-link">Model reference</a></Link>
              <Link href="/tutorials"><a className="nav-link">Tutorials</a></Link>
            </Nav>
            <Nav className="justify-content-end flex-grow-1 pe-3">
              <Link href=""><a className="nav-link"><i className={[styles.icon, "bi", "bi-slack"].join(" ")}></i></a></Link>
              <Link href=""><a className="nav-link"><i className={[styles.icon, "bi", "bi-github"].join(" ")}></i></a></Link>
              <Link href=""><a className="nav-link"><i className={[styles.icon, "bi", "bi-twitter"].join(" ")}></i></a></Link>
            </Nav>
          </Navbar.Collapse>
        </Container>
      </Navbar>
    )
  }
}