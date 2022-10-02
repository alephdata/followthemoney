/* global Prism */
import 'prismjs';

import * as React from 'react';
import copy from 'copy-to-clipboard';
import { Icon } from './Icon';

Prism.languages.markdoc = {
  tag: {
    pattern: /{%(.|\n)*?%}/i,
    inside: {
      tagType: {
        pattern: /^({%\s*\/?)(\w*|-)*\b/i,
        lookbehind: true
      },
      id: /#(\w|-)*\b/,
      string: /".*?"/,
      equals: /=/,
      number: /\b\d+\b/i,
      variable: {
        pattern: /\$[\w.]+/i,
        inside: {
          punctuation: /\./i
        }
      },
      function: /\b\w+(?=\()/,
      punctuation: /({%|\/?%})/i,
      boolean: /false|true/
    }
  },
  variable: {
    pattern: /\$\w+/i
  },
  function: {
    pattern: /\b\w+(?=\()/i
  }
};

export function Code({ children, 'data-language': language }) {
  const [copied, setCopied] = React.useState(false);
  const ref = React.useRef(null);

  React.useEffect(() => {
    if (ref.current) Prism.highlightElement(ref.current, false);
  }, [children]);

  React.useEffect(() => {
    if (copied) {
      copy(ref.current.innerText);
      const to = setTimeout(setCopied, 1000, false);
      return () => clearTimeout(to);
    }
  }, [copied]);

  const lang = language === 'md' ? 'markdoc' : language || 'markdoc';

  const lines =
    typeof children === 'string' ? children.split('\n').filter(Boolean) : [];

  return (
    <div className="code" aria-live="polite">
      <pre
        // Prevents "Failed to execute 'removeChild' on 'Node'" error
        // https://stackoverflow.com/questions/54880669/react-domexception-failed-to-execute-removechild-on-node-the-node-to-be-re
        key={children}
        ref={ref}
        className={`language-${lang}`}
      >
        {children}
      </pre>
      <button onClick={() => setCopied(true)}>
      <i className="bi bi-clipboard-plus"></i>
      </button>
      <style jsx>
        {`
          .code {
            position: relative;
          }
          .code button {
            appearance: none;
            position: absolute;
            color: inherit;
            background: var(--code-background);
            top: ${lines.length === 1 ? '17px' : '13px'};
            right: 11px;
            border-radius: 4px;
            border: none;
            font-size: 15px;
          }
        `}
      </style>
    </div>
  );
}
