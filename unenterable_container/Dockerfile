# syntax=docker/dockerfile:1
FROM python:3-slim AS build-env
COPY ./python_app /app
WORKDIR /app

FROM gcr.io/distroless/python3
COPY --from=build-env /app /app
WORKDIR /app
CMD ["app.py"]