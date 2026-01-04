FROM golang:1.16

WORKDIR /usr/src/backend

COPY . .

RUN go build

RUN go test ./...

EXPOSE 8080