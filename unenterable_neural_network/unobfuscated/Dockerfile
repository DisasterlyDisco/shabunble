# syntax=docker/dockerfile:1
FROM python:3.11-slim AS build-env

WORKDIR /app
COPY ../requirements.txt .

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

COPY ../classifier.py /app/
COPY ../cifar_net.pth /app/
COPY ../config.ini /app/

ENV PYTHONPATH="/opt/venv/lib/python3.11/site-packages"

CMD ["python", "classifier.py"]