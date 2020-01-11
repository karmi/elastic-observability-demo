# $ docker build --tag elastic/demo-elasticstack .
# $ docker run -it --publish 8000:8000 --rm elastic/demo-elasticstack
#
FROM golang:1-alpine AS Builder

WORKDIR /
COPY go.mod go.mod
COPY app.go app.go

RUN apk update && apk add --no-cache --quiet ca-certificates git

RUN CGO_ENABLED=0 GOOS=linux go build -mod=vendor -tags netgo -o /app app.go

FROM alpine

RUN apk update && apk add --no-cache --quiet ca-certificates curl

COPY --from=Builder /app /app

EXPOSE 8000
ENTRYPOINT ["/app"]
