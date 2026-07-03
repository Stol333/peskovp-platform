FROM python:3.12-slim

RUN groupadd --system app && useradd --system --gid app app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app/integrations/vpn

COPY integrations/vpn/src /app/integrations/vpn/src
COPY integrations/vpn/run_snapshot.py /app/integrations/vpn/run_snapshot.py

USER app

CMD ["python", "run_snapshot.py"]
