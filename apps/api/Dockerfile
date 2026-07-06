FROM python:3.12-slim

RUN groupadd --system app && useradd --system --gid app app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY apps/api/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt && \
    rm /tmp/requirements.txt

COPY apps/api /app/apps/api
COPY packages/vpn-routing /app/packages/vpn-routing

RUN mkdir -p /app/apps/api/logs && chown -R app:app /app

WORKDIR /app/apps/api
USER app

EXPOSE 8080

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
