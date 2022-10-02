import React from 'react';
import Nav from 'react-bootstrap/Nav';
import styles from '../styles/Sidebar.module.scss';

function Sidebar({headings}) {
  return (
    <Nav className={[styles.sidebar, "text-white", "bg-dark", "flex-column"]}>
        {headings.map((item) => (
          <Nav.Link key={Math.random()}>
            <svg className="bi me-2" width="16" height="16"><use xlinkHref="#speedometer2"></use></svg>
            {item.title}
          </Nav.Link>
        ))}      
    </Nav>
  );
}

export default Sidebar