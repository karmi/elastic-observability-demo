import logging
import os
import random
import time
import sys

from dotenv import load_dotenv
import elasticapm
import ecs_logging

load_dotenv()

logger = logging.getLogger("script")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)

if os.getenv("ELASTIC_APM_ENABLED", "") not in ["false" or "no"]:
    handler.setFormatter(
        ecs_logging.StdlibFormatter(
            exclude_fields=["log.original"],
            extra={"event": {"dataset": "demo.script"}},
            stack_trace_limit=0,  # Stack traces are in APM
        )
    )

logger.addHandler(handler)


@elasticapm.capture_span()
def process(payload):
    # Simulate errors (~ 10% calls)
    if random.randint(1, 100) > 90:
        raise Exception("Simulated processing error")

    with elasticapm.capture_span("Sleep"):
        # Simulate duration
        time.sleep(random.uniform(0, 1.0))

    # Custom logging
    logger.info(f"PROCESSED: Job #{payload}", extra={"iteration": payload})
    return True


def main():
    for i in range(1, 11):
        try:
            elasticapm.get_client().begin_transaction("cronjob")
            apm_result = "unknown"

            # Custom logging
            logger.debug(f"--> Processing job [{i}]")
            process(i)

            apm_result = "success"
        except Exception as e:
            logger.error(f"[!] Error when processing job [{i}]")
            elasticapm.get_client().capture_exception()
            apm_result = "failure"
        finally:
            elasticapm.get_client().end_transaction("cronjob", apm_result)


if __name__ == "__main__":
    elasticapm.instrument()
    elasticapm.Client()

    try:
        main()
    finally:
        elasticapm.get_client().close()
