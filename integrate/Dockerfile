FROM alpine:edge

RUN apk update && \
    apk add py3-icu py3-psycopg2 py3-gunicorn py3-cryptography py3-sqlalchemy

RUN apk add --virtual .build-deps gcc musl-dev python3-dev && \
    pip3 install python-levenshtein && \
    apk --purge del .build-deps

COPY setup.py /app/
COPY followthemoney_integrate /app/followthemoney_integrate/
RUN pip3 install -e /app
WORKDIR /app

ENV INTEGRATE_DATABASE_URI 'sqlite:///mydatabase.db'

EXPOSE 5000
ENTRYPOINT gunicorn -b :5000 --access-logfile - --error-logfile - followthemoney_integrate.views:app