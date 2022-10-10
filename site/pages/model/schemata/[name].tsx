import { GetStaticPropsContext } from 'next';
import { Model, defaultModel, Schema } from '@alephdata/followthemoney';
import SchemaExtends from '../../../components/SchemaExtends';
import SchemaProperties from '../../../components/SchemaProperties';

export function getStaticPaths() {
  const model = new Model(defaultModel);
  return {
    paths: Object.keys(model.schemata).map((name) => ({ params: { name } })),
    fallback: false,
  };
};

export function getStaticProps(context: GetStaticPropsContext) {
  return {
    props: { name: context?.params?.name },
  };
};

export default function SchemaPage({ name }: { name: string }) {
  const model = new Model(defaultModel);
  const schema = model.schemata[name] as Schema;

  return (
    <>
      <h1>{schema.label}</h1>
      {schema.description && <p className="lead">{schema.description}</p>}

      <SchemaExtends schema={schema} />
      <SchemaProperties schema={schema} />
    </>
  );
};
