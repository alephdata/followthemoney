import { Model, defaultModel } from '../src'

describe('ftm/PropertyType class', () => {
  const model = new Model(defaultModel);

  it('has description property', () => {
    const name = model.types['name'];
    expect(name.description).toContain('A name used for a person or company.');
  });
});
