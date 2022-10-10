import React from 'react';
import Nav from 'react-bootstrap/Nav';
import styles from '../styles/Sidebar.module.scss';

interface SidebarProps {
  headings: Array<{ title: string }>,
};

function Sidebar({headings}: SidebarProps) {
  return (
    <Nav className={`${styles.sidebar} text-white bg-dark flex-column`}>
        {headings.map((item) => (
          <Nav.Link key={item.title}>
            <svg className="bi me-2" width="16" height="16"><use xlinkHref="#speedometer2"></use></svg>
            {item.title}
          </Nav.Link>
        ))}      
    </Nav>
  );
}

export default Sidebar