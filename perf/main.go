// Copyright 2016 Nordstrom Inc., authors, and contributors <see AUTHORS file>
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

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
	target:   "/targets.txt",
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
	if config.target == "" {
		log.Fatal("target must be set")
	}
	if os.Getenv("BUCKET") != "" {
		config.bucket = os.Getenv("BUCKET")
	}
	// TODO: only works for aws buckets...
	if config.bucket == "" {
		log.Fatal("bucket must be set")
	}
	if os.Getenv("KEY") != "" {
		config.key = os.Getenv("KEY")
	}

	f, err := os.Open(config.target)
	if err != nil {
		log.Fatal(err)
	}
	defer f.Close()
	targeter, err := vegeta.NewEagerTargeter(f, nil, nil)
	if err != nil {
		log.Fatal(err)
	}

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

	_, err = svc.PutObject(params)
	if err != nil {
		log.Fatal(err)
	}
}
