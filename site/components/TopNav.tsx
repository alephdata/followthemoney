import React from 'react';
import Container from 'react-bootstrap/Container';
import Nav from "react-bootstrap/Nav";
import Navbar from "react-bootstrap/Navbar";
import Link from 'next/link';
export default class TopNav extends React.Component {
  render() {
    return (
      <Navbar bg="dark" variant="dark">
        <Container>
          <Navbar.Brand href="/">FtM</Navbar.Brand>
          <Nav className="main-nav">
            <Link href="/"><a className="nav-link">Home</a></Link>
            <Link href="/docs/introduction"><a className="nav-link">Docs</a></Link>
          </Nav>
        </Container>
      </Navbar>
    )
  }
}