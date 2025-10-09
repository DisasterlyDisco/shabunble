# syntax=docker/dockerfile:1
FROM python:3.11-slim AS build-env

WORKDIR /so/mazed/much/wow/app
COPY ../requirements.txt .

RUN python -m venv /theyll/never/know/opt/venv
ENV PATH="/theyll/never/know/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

COPY ../mazed/classifier.py /so/mazed/much/wow/app/
COPY ../cifar_net.pth /deepest/darkest/depth/
COPY ../config.ini /so/mazed/much/wow/app/

ENV PYTHONPATH="/theyll/never/know/opt/venv/lib/python3.11/site-packages"

CMD ["python", "classifier.py"]