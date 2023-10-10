import os
import random
import time

import redis

from flask import Flask, request, jsonify, make_response

import elasticapm
from elasticapm.contrib.flask import ElasticAPM

app = Flask(__name__)

# Configuration for ElasticAPM
app.config["ELASTIC_APM"] = {"SERVICE_NAME": "demo-service"}
apm = ElasticAPM(app)

# Redis configuration
redis_host, redis_port = os.getenv("REDIS_URL").split(":")
redis_pwd = os.getenv("REDIS_PWD")
r = redis.Redis(host=redis_host, port=redis_port, password=redis_pwd)


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
            time.sleep(random.randint(0, 10))

    # Record page view
    try:
        i = r.incr("pageviews")
    except redis.RedisError as e:
        apm.capture_exception()
        return "Internal Server Error", 500

    return f"Hello! This page has been viewed {i} times.", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
