import React from 'react';

function Sidebar({headings}) {
  return (
    <nav>
      <ul>
        {headings.map((item) => (
          <li key={item.title}>
            <a className="nav-link" href={`#${item.title}`}>{item.title}</a>
          </li>
        ))}
      </ul>
    </nav>
  );
}

export default Sidebar