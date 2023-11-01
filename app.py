import logging
import os
import random
import time
import sys

import redis

from flask import Flask, request, jsonify, make_response

import elasticapm
from elasticapm.contrib.flask import ElasticAPM
import ecs_logging

app = Flask(__name__)

# ElasticAPM configuration
apm = ElasticAPM(app)

# Redis configuration
redis_host, redis_port = os.getenv("REDIS_URL", "").split(":")
redis_pwd = os.getenv("REDIS_PWD")
r = redis.Redis(host=redis_host, port=redis_port, password=redis_pwd)

# Logging
logger = logging.getLogger("app")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)

if os.getenv("ELASTIC_APM_ENABLED", "") not in ["false" or "no"]:
    handler.setFormatter(
        ecs_logging.StdlibFormatter(
            exclude_fields=["log.original"],
            extra={"event": {"dataset": "demo.app"}},
            stack_trace_limit=0,  # Stack traces are in APM
        )
    )

logger.addHandler(handler)


@app.route("/status", methods=["GET"])
def status():
    return "OK", 200


@app.route("/", methods=["GET"])
def index():
    # Simulate server errors (5% requests)
    if random.randint(1, 100) > 95:
        try:
            raise Exception("Simulated server error")
        except Exception as e:
            apm.capture_exception()
            raise e

    # Simulate slow responses (10% requests)
    if random.randint(1, 100) > 90:
        with elasticapm.capture_span("Sleep"):
            time.sleep(random.randint(0, 5))

    # Record page view
    try:
        i = r.incr("pageviews")
    except redis.RedisError as e:
        apm.capture_exception()
        return "Internal Server Error", 500

    # Custom logging
    if i % 10 == 0:
        logger.info(f"Page viewed {i} times", extra={"iteration": i})

    return f"Hello! This page has been viewed {i} times.", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
