# Observability with the Elastic Stack

This repository contains demo configuration for monitoring a typical web service
with the [Elastic Stack](https://www.elastic.co/products).

-----

Generate certificates for the services using [`elasticsearch-certutil`](https://www.elastic.co/guide/en/elasticsearch/reference/current/certutil.html):

    docker-compose --file certificates-create.yml up

> NOTE: On Linux, change the permissions with `sudo chown -R $USER certificates`.

Verify that the certificates have been succesfully created:

    ls -la ./certificates

Download the dependencies for the Go application:

    go mod tidy
    go mod vendor

> NOTE: When you change the application source in `app.go`, remove the container with `docker-compose stop app && docker-compose rm --force app` and start it again with `docker-compose up app --build --force-recreate --detach`.

Launch the services with [Docker Compose](https://docs.docker.com/compose/):

    docker-compose up --remove-orphans --detach

> NOTE: To bind Nginx on standard ports, export the corresponding environment variables: `NGINX_HTTP_PORT=80 NGINX_HTTPS_PORT=443 docker-compose up --remove-orphans --detach`.

Inspect the status of the services:

    docker-compose ps

Inspect the log output of the services:

    docker-compose logs -f

Wait until Elasticsearch is running, and set the password for Kibana:

    until docker inspect demo-elasticsearch-1 > /dev/null 2>&1 && [[ $(docker inspect -f '{{ .State.Health.Status }}' demo-elasticsearch-1) == "healthy" ]]; do echo -n '.'; sleep 1; done; source .env
    curl -s -X POST --cacert ./certificates/ca/ca.crt -u "elastic:${ELASTIC_PASSWORD}" -H "Content-Type: application/json" https://localhost:9200/_security/user/kibana_system/_password -d "{\"password\":\"${ELASTIC_PASSWORD}\"}"


Once Kibana is running, navigate to the "APM" page at <https://localhost:5601/app/apm/services>, logging in as `elastic:elastic` and add the APM integration, following the [documentation](https://www.elastic.co/guide/en/apm/guide/current/apm-server-configuration.html): just click _“Save & Continue”_ and choose _“Add Elastic Agent Later”_.

Drive some traffic to the application (it will randomly fail 5% requests and simulate latency for 10% of requests):

    for i in `seq 1 100`; do curl -k -s https://localhost:4430; sleep 0.1; done

Alternatively, use a tool like [`siege`](https://github.com/JoeDog/siege), [`wrk`](https://github.com/wg/wrk) or [`hey`](https://github.com/rakyll/hey):

    siege --time=15s --verbose https://localhost:4430
    wrk --duration 15s --latency https://localhost:4430
    hey -z 15s https://localhost:4430

To access the services locally, pass the certificate authority to your client:

    curl -i --cacert certificates/ca/ca.crt https://localhost:4430

> NOTE: On Mac OS X, you may need to add the certificate to the Keychain with `security add-trusted-cert -p ssl certificates/ca/ca.crt`. To remove it, run `security remove-trusted-cert certificates/ca/ca.crt`.

> NOTE: To allow accessing the services in Google Chrome, enable the `chrome://flags/#allow-insecure-localhost` setting.

To remove the containers, run:

    docker-compose down --volumes
