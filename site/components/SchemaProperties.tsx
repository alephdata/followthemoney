import { useState, ChangeEvent } from 'react';
import c from 'classnames';
import { Schema } from '@alephdata/followthemoney';
import Table from 'react-bootstrap/table';

export default function SchemaProperties({ schema }: { schema: Schema }) {
  const properties = Array.from(schema.getProperties().values()).sort((a, b) =>
    a.name.localeCompare(b.name)
  );

  const [showInherited, setShowInherited] = useState(false);
  const handleCheckboxChange = (event: ChangeEvent<HTMLInputElement>) => setShowInherited(event.target.checked);

  return (
    <>
      <div className="d-flex justify-content-between align-items-center">
        <h2 className="mb-0">Properties</h2>

        <label>
          <input
            type="checkbox"
            onChange={handleCheckboxChange}
          />
          Show inherited
        </label>
      </div>

      <Table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Info</th>
            <th>Type</th>
          </tr>
        </thead>

        <tbody>
          {
            properties.map((prop) => (
                <tr
                  key={prop.qname}
                  className={c(prop.schema.name !== schema.name && 'bg-light')}
                  hidden={!showInherited && prop.schema.name !== schema.name}
                >
                  <td>
                    <code>{prop.name}</code>
                  </td>
                  <td>
                    {prop.label}
                  </td>
                  <td>
                    {prop.type.name}
                  </td>
                </tr>
            ))
          }
        </tbody>
      </Table>
    </>
  );
};