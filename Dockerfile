# syntax=docker/dockerfile:1

# Use the official Python image as the base image.
ARG PYTHON_VERSION=3.10.11
FROM python:${PYTHON_VERSION}-slim as base
RUN apt-get update && \
    apt-get install -y gcc zlib1g-dev libjpeg-dev tesseract-ocr 
# Set environment variables to control Python behavior.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create a working directory for the application.
WORKDIR /app

# Create a non-privileged user that the app will run under.
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser
RUN chown -R appuser:appuser /app
RUN chmod -R 755 /app
# Install Pillow dependencies including zlib and libjpeg.
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install --no-cache-dir -r requirements.txt

# Switch to the non-privileged user to run the application.
USER appuser

# Copy the source code into the container.
COPY . .

# Expose the port that the application listens on.
EXPOSE 8000

# Run the application.
CMD python3 main.py
