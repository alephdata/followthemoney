import os
import json
from redis import Redis
from normality import stringify


class Cache(object):

    def get(self, key):
        return None

    def has(self, key):
        return self.get(key) is not None

    def store(self, key, value):
        pass


class RedisCache(Cache):
    EXPIRE = 84600 * 90
    URL = os.environ.get('ENRICH_REDIS_URL')

    def __init__(self):
        self.redis = Redis.from_url(self.URL)

    def _prefix_key(self, key):
        return 'ftm:enrich:%s' % stringify(key)

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
