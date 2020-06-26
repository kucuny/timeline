FROM python:3.8.3-alpine3.11

WORKDIR /app
COPY backend/requirements/* ./requirements/
RUN apk update \
    && apk add postgresql-dev musl-dev libffi-dev make zlib-dev jpeg-dev gcc \
    && pip install -r requirements/base.txt

ENV PYTHONUNBUFFERED 1

#CMD ['uvicorn', 'config.asgi:application', '--port', '12095', '--reload']
CMD ["python", "/app/manage.py", "runserver", "0:8000"]