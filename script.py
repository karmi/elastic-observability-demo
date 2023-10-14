import random
import time

from dotenv import load_dotenv
import elasticapm

load_dotenv()


@elasticapm.capture_span()
def process(payload):
    # Simulate errors (~ 10% calls)
    if random.randint(1, 100) > 90:
        raise Exception("Simulated processing error")

    with elasticapm.capture_span("Sleep"):
        # Simulate duration
        time.sleep(random.uniform(0, 1.0))

    print(f"    PROCESSED: {payload}")
    return True


def main():
    for i in range(1, 11):
        try:
            elasticapm.get_client().begin_transaction("cronjob")
            apm_result = "unknown"

            print(f"--> Processing job [{i}]")
            process(f"Job #{i}")

            apm_result = "success"
        except Exception as e:
            print(f"[!] Error when processing job [{i}]")
            elasticapm.get_client().capture_exception()
            apm_result = "failure"
        finally:
            elasticapm.get_client().end_transaction("cronjob", apm_result)


if __name__ == "__main__":
    elasticapm.instrument()
    elasticapm.Client(enabled=True)

    try:
        main()
    finally:
        elasticapm.get_client().close()
