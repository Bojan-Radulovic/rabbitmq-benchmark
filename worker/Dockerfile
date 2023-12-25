FROM python:3.9.5-slim as worker-base

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
    --mount=type=bind,source=worker/requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

USER appuser

COPY worker .

CMD ["python", "worker.py"]
