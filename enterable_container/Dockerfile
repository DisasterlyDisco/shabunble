# syntax=docker/dockerfile:1
FROM python:3-slim
COPY ./python_app /app
WORKDIR /app
RUN adduser boomer
USER boomer
CMD ["python", "app.py"]
