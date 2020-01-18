package main

import (
	"errors"
	"fmt"
	"io"
	"log"
	"math/rand"
	"net/http"
	"os"
	"time"

	"github.com/go-redis/redis"

	"go.elastic.co/apm"
	"go.elastic.co/apm/module/apmgoredis"
	"go.elastic.co/apm/module/apmhttp"
)

const (
	listenAddr = "0.0.0.0:8000"
)

var (
	rdb = redis.NewClient(
		&redis.Options{Addr: os.Getenv("REDIS_URL"), Password: os.Getenv("REDIS_PWD")})
)

func main() {
	log.SetFlags(0)
	rand.Seed(time.Now().UnixNano())

	http.Handle(
		"/",
		apmhttp.Wrap(
			http.HandlerFunc(
				func(w http.ResponseWriter, req *http.Request) {
					// Handle /status
					//
					if req.URL.Path == "/status" {
						io.WriteString(w, "OK")
						return
					}

					// Simulate server errors (5% requests)
					//
					if rand.Intn(100) > 95 {
						apm.CaptureError(req.Context(), errors.New("Simulated server error")).Send()
						log.Println("Service unavailable")
						http.Error(w, "Service Unavailable", http.StatusServiceUnavailable)
						return
					}

					// Record page view
					//
					client := apmgoredis.Wrap(rdb).WithContext(req.Context())
					i, err := client.Incr("pageviews").Result()
					if err != nil {
						apm.CaptureError(req.Context(), err).Send()
						log.Println("Redis error:", err)
						http.Error(w, "Internal Server Error", http.StatusInternalServerError)
						return
					}

					// Return response
					//
					fmt.Fprintf(w, "Hello! This page has been viewed %d times.\n", i)
				},
			),
		),
	)

	log.Printf("Server starting at %s...", listenAddr)
	if err := http.ListenAndServe(listenAddr, nil); err != nil && err != http.ErrServerClosed {
		log.Fatal("Unable to start server")
		os.Exit(1)
	}
}
