Generate certificates for the services using `elasticsearch-certutil`:

    docker-compose --file certificates-create.yml up

> NOTE: On Linux, change the permissions with `sudo chown -R $USER certificates`.

Download the dependencies for the application:

    go mod vendor

Launch the service with Docker Compose:

    docker-compose up --remove-orphans

Wait until Kibana is running:

    until docker inspect demo_kibana_1 > /dev/null 2>&1 && [[ $(docker inspect -f '{{ .State.Health.Status }}' demo_kibana_1) == "healthy" ]]; do echo -n '.'; sleep 5; done; echo -e "\nKIBANA IS RUNNING\n"

Open Kibana at <http://localhost:5601> and drive some traffic to the application:

    for i in `seq 1 100`; do curl -s http://localhost:8080; sleep 0.1; done

Alternatively, use a tool like `siege`, `wrk` or `hey`:

    siege --time=15s --internet http://localhost:8080
    wrk --duration 15s  --latency http://localhost:8080
    hey -z 15s http://localhost:8080

To remove the containers, run:

    docker-compose down --volumes
