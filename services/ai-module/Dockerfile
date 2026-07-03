FROM python:3.12-slim

RUN groupadd --system app && useradd --system --gid app app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app/services/ai-module

COPY services/ai-module/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt && \
    rm /tmp/requirements.txt

COPY services/ai-module /app/services/ai-module

RUN mkdir -p /app/services/ai-module/logs && chown -R app:app /app

USER app

EXPOSE 8787

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8787"]
