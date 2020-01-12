# $ go mod vendor
# $ docker build --tag elastic/demo-elasticstack .
# $ docker run -it --publish 8000:8000 --rm elastic/demo-elasticstack
#
FROM golang:1-alpine AS Builder

WORKDIR /app

RUN apk update && apk add --no-cache --quiet ca-certificates git

COPY go.mod go.sum ./
COPY vendor ./vendor

COPY app.go ./
RUN CGO_ENABLED=0 GOOS=linux go build -mod=vendor -tags netgo -o /app/server app.go

FROM alpine

RUN apk update && apk add --no-cache --quiet ca-certificates curl

COPY --from=Builder /app/server /server

EXPOSE 8000
ENTRYPOINT ["/server"]
