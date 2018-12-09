FROM python:3.6-alpine

COPY app.py Pipfile Pipfile.lock /app/
COPY templates /app/templates/
WORKDIR /app

ENV DATAVAULT_URI 'sqlite:///mydatabase.db'

RUN apk update && \
    apk add postgresql-libs && \
    apk add --virtual .build-deps gcc musl-dev postgresql-dev && \
    pip install pipenv gunicorn && \
    pipenv install --system --deploy && \
    apk --purge del .build-deps

EXPOSE 5000
ENTRYPOINT gunicorn -b :5000 --access-logfile - --error-logfile - app:app