FROM python:3.9.5-slim as app-base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=web/requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

USER appuser

USER root
RUN apt-get update && apt-get install -y apache2-utils
USER appuser

COPY web .

EXPOSE 5000

CMD python3 -m flask run --host=0.0.0.0
