# $ docker build -t elastic-observability-demo-app -f Dockerfile .
# $ docker run -it --rm --env REDIS_URL=...  --publish 8000:8000 elastic-observability-demo-app
#
# Cf. <https://testdriven.io/blog/docker-best-practices>

FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install curl for healthcheck
RUN apt-get update && \
   apt-get install --yes --no-install-recommends curl && \
   apt-get clean && \
   rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app.py /app/

ENV PORT=${PORT:-8000}

# https://cloud.google.com/run/docs/tips/python#optimize_gunicorn
#
ENTRYPOINT /usr/local/bin/gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 'app:app'
