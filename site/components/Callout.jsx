import * as React from 'react';

const TYPE_MAP = {
  note: {
    icon: 'information-circle',
    iconColor: '#8792a2'
  },
  warning: {
    icon: 'bi-exclamation-circle-fill',
    iconColor: '#d97917'
  },
  check: {
    icon: 'checkmark-circle',
    iconColor: 'var(--black)'
  },
  error: {
    icon: 'warning',
    iconColor: '#ed5f74'
  }
};

export function Callout({ title, children, type }) {
  const { icon, iconColor } = TYPE_MAP[type] || TYPE_MAP.note;

  return (
    <div className="callout">
      <div className={`flex content ${type}`}>
        <div className="flex icon">
            <i className={`bi ${icon}`}></i>
        </div>
        <div className="flex column">
          <strong>{title}</strong>
          <span>{children}</span>
        </div>
      </div>
      <style jsx>
        {`
          .callout {
            padding: 0.5rem 0 2rem;
          }
          .content {
            color: var(--dark);
            background: var(--code-background);
            border: 3px solid var(--code-border);
            line-height: 20px;
            padding: 12px 20px;
            border-radius: 4px;
          }
          .icon {
            padding-right: 8px;
            align-items: center;
          }
          .callout :global(p:first-of-type) {
            padding: 0;
          }
          .error {
            background-color: #dc3545
          }
          .warning {
            background-color: rgba(var(--bs-warning-rgb), .15);
            border: 1px solid rgba(var(--bs-warning-rgb), .75);
            border-left: 5px solid rgba(var(--bs-warning-rgb), .75);
          }
          .note {
            background-color: rgba(var(--bs-info-rgb), .15);
            border: 1px solid rgba(var(--bs-info-rgb), .75);
            border-left: 5px solid rgba(var(--bs-info-rgb), .75);
          }
          .check {
            background-color: #198754;
          }
        `}
      </style>
    </div>
  );
}
