package main

import (
	"bytes"
	"crypto/tls"
	"encoding/json"
	"log"
	"net/http"
	"os"
	"strconv"
	"time"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/s3"
	"github.com/foolusion/certs"
	"github.com/tsenart/vegeta/lib"
)

var config = struct {
	rate     uint64
	duration time.Duration
	target   string
	bucket   string
	key      string
}{
	rate:     100,
	duration: time.Minute,
	target:   "http://internal-46111-CXAR-ATO-Elwin-LB-2059848312.us-west-2.elb.amazonaws.com/epe/123",
	bucket:   "cxar-ato-team",
	key:      "elwin/perf.json",
}

func main() {
	if os.Getenv("RATE") != "" {
		if i, err := strconv.Atoi(os.Getenv("RATE")); err == nil {
			config.rate = uint64(i)
		}
	}
	if os.Getenv("DURATION") != "" {
		if dur, err := time.ParseDuration(os.Getenv("DURATION")); err == nil {
			config.duration = dur
		}
	}
	if os.Getenv("TARGET") != "" {
		config.target = os.Getenv("TARGET")
	}
	if os.Getenv("BUCKET") != "" {
		config.bucket = os.Getenv("BUCKET")
	}
	if os.Getenv("KEY") != "" {
		config.key = os.Getenv("KEY")
	}

	targeter := vegeta.NewStaticTargeter(vegeta.Target{
		Method: "GET",
		URL:    config.target,
	})

	attacker := vegeta.NewAttacker()

	var metrics vegeta.Metrics
	for res := range attacker.Attack(targeter, config.rate, config.duration) {
		metrics.Add(res)
	}
	metrics.Close()

	pool := certs.Pool
	client := &http.Client{
		Transport: &http.Transport{
			Proxy: http.ProxyFromEnvironment,
			TLSClientConfig: &tls.Config{
				RootCAs: pool,
			},
		},
	}

	conf := &aws.Config{HTTPClient: client, Region: aws.String("us-west-2")}
	sess := session.New(conf)
	svc := s3.New(sess)

	var buf bytes.Buffer
	enc := json.NewEncoder(&buf)
	enc.Encode(metrics)

	params := &s3.PutObjectInput{
		Bucket: aws.String(config.bucket),
		Key:    aws.String(config.key + "(" + time.Now().String() + ")"),
		Body:   bytes.NewReader(buf.Bytes()),
	}

	_, err := svc.PutObject(params)
	if err != nil {
		log.Fatal(err)
	}
}
