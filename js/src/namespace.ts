import crypto from 'crypto';

export class Namespace {
  private separator: string = '.'
  private namespaceKey: string

  constructor(namespaceKey: string) {
    this.namespaceKey = namespaceKey;
  }

  parse(id: string) {
    if (id.includes(this.separator)) {
      return id.split(this.separator);
    }
    return [null, id];
  }

  signature(id: string) {
    return crypto.createHmac('sha1', this.namespaceKey)
      .update(id)
      .digest('hex');
  }

  sign(id: string) {
    const [namespace, entityId] = this.parse(id);
    if (!this.namespaceKey.length) {
      return entityId;
    }
    if (!entityId) {
      return null;
    }
    const digest = this.signature(entityId);

    return [digest, entityId].join(this.separator);
  }
}
