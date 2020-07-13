FROM python:3.8.3-alpine3.11

WORKDIR /app
COPY backend/requirements/* ./requirements/
RUN apk update \
    && apk add postgresql-dev musl-dev libffi-dev make zlib-dev jpeg-dev gcc \
    && pip install -r requirements/base.txt

ENV PYTHONUNBUFFERED 1

EXPOSE 12095

ENTRYPOINT ["uvicorn", "config.asgi:application", "--host", "0.0.0.0", "--port", "12095", "--reload"]
