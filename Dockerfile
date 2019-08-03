FROM alpine:3.10

RUN apk add --no-cache python3 py3-icu py3-lxml py3-cryptography libpq leveldb
RUN apk add --no-cache --virtual=build_deps python3-dev g++ musl-dev leveldb-dev postgresql-dev && \
    pip3 install --no-cache-dir python-levenshtein plyvel psycopg2-binary && \
    apk del build_deps

RUN addgroup -g 1000 app && \
    adduser -D -u 1000 -G app app

RUN pip3 install --no-cache-dir -U pip setuptools six
RUN mkdir -p /opt/followthemoney
COPY README.md LICENSE babel.cfg setup.py setup.cfg /opt/followthemoney/
COPY followthemoney /opt/followthemoney/followthemoney/
COPY tests /opt/followthemoney/tests/
RUN pip3 install --no-cache-dir -e /opt/followthemoney
