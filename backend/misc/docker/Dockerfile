FROM python:3.8-alpine

WORKDIR /usr/src/web/app
COPY backend/requirements/* ./requirements/
RUN apk update \
    && apk add postgresql-dev musl-dev libffi-dev make zlib-dev jpeg-dev gcc \
    && pip install -r requirements/dev.txt

ENV PYTHONUNBUFFERED 1

CMD ['python', '/usr/src/web/app/manage.py', 'runserver', '0:8000']