import Link from 'next/link';
import { Schema } from '@alephdata/followthemoney';

export default function SchemaExtends({ schema }: { schema: Schema }) {
  const parents = schema.getExtends();

  return (
    <>
      <h2>Extends</h2>

      {
        parents.length > 0 && (
          <>
            <p>The {schema.label} schema extends the following schemata:</p>
            <ul>
              {parents.map((parent) => (
                <li key={parent.name}>
                  <Link href={`/model/schemata/${parent.name}`}>{parent.label}</Link>
                </li>
              ))}
            </ul>
          </>
        )
      }

      {
        parents.length <= 0 && (
          <p>The {schema.label} schema does not extend any other schemata.</p>
        )
      }
    </>
  );
};