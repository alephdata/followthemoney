FROM alpine:3.11

RUN apk add --no-cache python3 py3-icu py3-lxml py3-cryptography libpq leveldb curl make
RUN apk add --no-cache --virtual=build_deps python3-dev g++ musl-dev libffi-dev leveldb-dev postgresql-dev && \
    pip3 install --upgrade --no-cache-dir cryptography python-levenshtein plyvel psycopg2-binary && \
    apk del build_deps

RUN addgroup -g 1000 app && \
    adduser -D -u 1000 -G app app

RUN pip3 install --no-cache-dir -U pip setuptools six
RUN mkdir -p /opt/followthemoney
WORKDIR /opt/followthemoney
COPY README.md LICENSE babel.cfg setup.py setup.cfg /opt/followthemoney/
COPY followthemoney /opt/followthemoney/followthemoney/
COPY tests /opt/followthemoney/tests/
COPY enrich /opt/followthemoney/enrich/
RUN pip3 install --no-cache-dir -e /opt/followthemoney
RUN pip3 install --no-cache-dir -e /opt/followthemoney/enrich

COPY docs /docs/
WORKDIR /docs

CMD ftm