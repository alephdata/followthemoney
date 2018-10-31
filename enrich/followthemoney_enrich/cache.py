import json
from datetime import datetime
from normality import stringify


class Cache(object):

    def get(self, key):
        return None

    def has(self, key):
        return self.get(key) is not None

    def store(self, key, value):
        pass


class DatasetTableCache(Cache):

    def __init__(self, table):
        self.table = table

    def store(self, key, value):
        key = stringify(key)
        if key is not None:
            self.table.upsert({
                'key': key,
                'value': json.dumps(value),
                'timestamp': datetime.utcnow()
            }, ['key'])

    def get(self, key):
        key = stringify(key)
        data = self.table.find_one(key=key)
        if data is not None:
            value = data.get('value')
            return json.loads(value)


class RedisCache(Cache):
    EXPIRE = 84600 * 90

    def __init__(self, redis):
        self.redis = redis

    def _prefix_key(self, key):
        return 'enrich:%s' % stringify(key)

    def store(self, key, value):
        key = self._prefix_key(key)
        self.redis.set(key, json.dumps(value), ex=self.EXPIRE)

    def get(self, key):
        value = self.redis.get(self._prefix_key(key))
        if value is not None:
            return json.loads(value)

    def has(self, key):
        key = self._prefix_key(key)
        return self.redis.exists(key)
