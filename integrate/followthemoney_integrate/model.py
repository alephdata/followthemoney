import json
from banal import ensure_list
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy import Column, MetaData, String, Integer, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import sessionmaker
from followthemoney import model
from followthemoney.util import get_entity_id

from followthemoney_integrate import settings

now = datetime.utcnow
engine = create_engine(settings.DATABASE_URI)
metadata = MetaData(bind=engine)
Session = sessionmaker(bind=engine)
Base = declarative_base(bind=engine, metadata=metadata)


class Entity(Base):
    id = Column(String(255), primary_key=True)
    schema = Column(String(255))
    origin = Column(String(255))
    properties = Column(String)
    context = Column(String)
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now, onupdate=now)

    @declared_attr
    def __tablename__(cls):
        return settings.DATABASE_PREFIX + '_entity'

    def to_dict(self):
        data = json.loads(self.context)
        data['id'] = self.id
        data['schema'] = self.schema
        data['properties'] = json.loads(self.properties)
        return data

    @hybrid_property
    def proxy(self):
        if not hasattr(self, '_proxy'):
            self._proxy = model.get_proxy(self.to_dict())
        return self._proxy

    @proxy.setter
    def proxy(self, proxy):
        self._proxy = proxy
        self.id = proxy.id
        self.schema = proxy.schema.name
        self.properties = json.dumps(proxy.properties)
        self.context = json.dumps(proxy.context)

    @classmethod
    def save(cls, session, origin, proxy):
        obj = cls.by_id(session, proxy.id)
        if obj is None:
            obj = cls()
            obj.origin = origin
        obj.proxy = proxy
        session.add(obj)
        return obj

    @classmethod
    def by_id(cls, session, entity_id):
        if entity_id is None:
            return
        q = session.query(cls)
        q = q.filter(cls.id == entity_id)
        return q.first()

    @classmethod
    def all(cls, session):
        q = session.query(cls)
        for entity in q.yield_per(10000):
            yield entity

    @classmethod
    def by_ids(cls, session, entity_ids):
        entity_ids = ensure_list(entity_ids)
        if not len(entity_ids):
            return {}
        q = session.query(cls)
        q = q.filter(cls.id.in_(entity_ids))
        return {e.id: e for e in q}

    # @classmethod
    # def by_priority(cls, session, user):
    #     dq = session.query(Decision)


class Match(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    left = Column(String(255))
    right = Column(String(255))
    score = Column(Float)
    judgement = Column(String(5))
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now, onupdate=now)

    @declared_attr
    def __tablename__(cls):
        return settings.DATABASE_PREFIX + '_match'

    @classmethod
    def save(cls, session, left, right, score=None, judgement=None):
        left = get_entity_id(left)
        right = get_entity_id(right)
        left, right = cls.keys(left, right)
        obj = cls.by_keys(session, left, right)
        if obj is None:
            obj = cls()
            obj.left = left
            obj.right = right
        if score is not None:
            obj.score = score
        if judgement is not None:
            obj.judgement = judgement
        session.add(obj)
        return obj

    @classmethod
    def by_keys(cls, session, left, right):
        left, right = cls.keys(left, right)
        q = session.query(cls)
        q = q.filter(cls.left == left)
        q = q.filter(cls.right == right)
        return q.first()

    @classmethod
    def keys(cls, left, right):
        left = get_entity_id(left)
        right = get_entity_id(right)
        max_id = max((left, right))
        min_id = min((left, right))
        return (min_id, max_id)

    @classmethod
    def all(cls, session):
        q = session.query(cls)
        for match in q.yield_per(10000):
            yield match


class Vote(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    left = Column(String(255))
    right = Column(String(255))
    user = Column(String(255))
    judgement = Column(String(5))
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now, onupdate=now)

    @declared_attr
    def __tablename__(cls):
        return settings.DATABASE_PREFIX + '_vote'
