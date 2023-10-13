# Observability with the Elastic Stack

This repository contains demo configuration for monitoring a typical web service
with the [Elastic Stack](https://www.elastic.co/products).

-----

### 1. Generate Certificates

Generate certificates for the services using [`elasticsearch-certutil`](https://www.elastic.co/guide/en/elasticsearch/reference/current/certutil.html):

    docker compose --file certificates-create.yml up

> NOTE: On Linux, change the permissions with `sudo chown -R $USER certificates`.

Verify that the certificates have been succesfully created:

    ls -la ./certificates

### 2. Launch the Services

Launch the services with [Docker Compose](https://docs.docker.com/compose/):

    docker compose up --remove-orphans --detach

> NOTE: To bind Nginx on standard ports, export the corresponding environment variables: `NGINX_HTTP_PORT=80 NGINX_HTTPS_PORT=443 docker compose up --remove-orphans --detach`.

> NOTE: When you change the source in `app.py`, rebuild it with `docker compose up app --build --force-recreate --detach app`.

### 3. Set the Kibana Password

Wait until Elasticsearch is running, and set the password for Kibana:

    until docker inspect demo-elasticsearch-1 > /dev/null 2>&1 && [[ $(docker inspect -f '{{ .State.Health.Status }}' demo-elasticsearch-1) == "healthy" ]]; do echo -n '.'; sleep 1; done; source .env
    curl -s -X POST --cacert ./certificates/ca/ca.crt -u "elastic:${ELASTIC_PASSWORD}" -H "Content-Type: application/json" https://localhost:9200/_security/user/kibana_system/_password -d "{\"password\":\"${ELASTIC_PASSWORD}\"}"

### 4. Inspect the Results

Navigate to the "APM" Kibana page at <https://localhost:5601/app/apm/services>, logging in as `elastic:elastic`.

Drive some traffic to the application (it will randomly fail 5% requests and simulate latency for 10% of requests):

    for i in `seq 1 100`; do curl -k -s 'https://localhost:4430'; echo; done

Alternatively, use a tool like [`siege`](https://github.com/JoeDog/siege), [`wrk`](https://github.com/wg/wrk) or [`hey`](https://github.com/rakyll/hey):

    siege --time=15s --verbose https://localhost:4430
    wrk --duration 15s --latency https://localhost:4430
    hey -z 15s https://localhost:4430

To access the services locally, pass the certificate authority to your client:

```bash
curl -i --cacert certificates/ca/ca.crt https://localhost:4430
```

```python
import requests
r = requests.get('https://localhost:4430', verify='certificates/ca/ca.crt')
print(r.text)
```

> NOTE: On Mac OS X, you may need to add the certificate to the Keychain with `security add-trusted-cert -p ssl certificates/ca/ca.crt`. To remove it, run `security remove-trusted-cert certificates/ca/ca.crt`.

> NOTE: To allow accessing the services in Google Chrome, enable the `chrome://flags/#allow-insecure-localhost` setting.

-----

## Troubleshooting

To inspect the status of the services:

    docker compose ps

To inspect the log output of the services, eg. Elasticsearch:

    docker compose logs -f elasticsearch

## Deleting the Environment

To remove the containers, run:

    docker compose down --volumes --remove-orphans
