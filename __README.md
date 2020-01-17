# Observability with the Elastic Stack

This repository contains demo configuration for monitoring a typical web service
with the [Elastic Stack](https://www.elastic.co/products).

-----

Generate certificates for the services using [`elasticsearch-certutil`](https://www.elastic.co/guide/en/elasticsearch/reference/current/certutil.html):

    docker-compose --file certificates-create.yml up

> NOTE: On Linux, change the permissions with `sudo chown -R $USER certificates`.

Download the dependencies for the Go application:

    go mod vendor

> NOTE: When you change the application source in `app.go`, rebuild the service image with `docker-compose build app`.

Launch the services with [Docker Compose](https://docs.docker.com/compose/):

    docker-compose up --remove-orphans --detach

> NOTE: To bind Nginx on standard ports, export the corresponding environment variables: `NGINX_HTTP_PORT=80 NGINX_HTTPS_PORT=443 docker-compose up --remove-orphans --detach`.

> NOTE: To start a different version of the stack, export the environment variable: `VERSION=7.6-SNAPSHOT docker-compose up --remove-orphans --detach`.

Inspect the status of the services:

    docker-compose ps

Inspect the log output of the services:

    docker-compose logs -f

Wait until Kibana is running:

    until docker inspect demo_kibana_1 > /dev/null 2>&1 && [[ $(docker inspect -f '{{ .State.Health.Status }}' demo_kibana_1) == "healthy" ]]; do echo -n '.'; sleep 5; done; echo -e "\nKIBANA IS RUNNING\n"

Open Kibana at <https://localhost:5601> and drive some traffic to the application:

    for i in `seq 1 100`; do curl -k -s https://localhost:4430; sleep 0.1; done

Alternatively, use a tool like [`siege`](https://github.com/JoeDog/siege), [`wrk`](https://github.com/wg/wrk) or [`hey`](https://github.com/rakyll/hey):

    siege --time=15s --verbose https://localhost:4430
    wrk --duration 15s --latency https://localhost:4430
    hey -z 15s https://localhost:4430

To access the services locally, pass the certificate authority to your client:

    curl -i --cacert certificates/ca/ca.crt https://localhost:4430

> NOTE: On Mac OS X, you may need to add the certificate to the Keychain with `security add-trusted-cert -p ssl certificates/ca/ca.crt`. To remove it, run `security remove-trusted-cert certificates/ca/ca.crt`.

> NOTE: To allow accessing the services in recent versions of Google Chrome, enable the `chrome://flags/#allow-insecure-localhost` setting.

To remove the containers, run:

    docker-compose down --volumes
