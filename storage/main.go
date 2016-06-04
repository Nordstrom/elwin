package main

import (
	"fmt"
	"html/template"
	"log"
	"net/http"
	"net/url"
	"os"
	"os/signal"
	"syscall"

	"gopkg.in/mgo.v2"
	"gopkg.in/mgo.v2/bson"
)

var cfg = struct {
	dbURL string
	addr  string
	db    string
	coll  string

	// computed
	session *mgo.Session
}{}

type namespace struct {
	Name              string       `bson:"name" json:"name"`
	GroupIDs          []string     `bson:"group_ids" json:"groupIDs"`
	Units             []string     `bson:"units" json:"units"`
	NumSegments       int          `bson:"num_segments" json:"numSegments"`
	AvailableSegments []int        `bson:"available_segments" json:"availableSegments"`
	Experiments       []experiment `bson:"experiments" json:"experiments"`
}

type experiment struct {
	Name       string                 `bson:"name" json:"name"`
	Definition map[string]interface{} `bson:"definition" json:"definition"`
	Segments   []int                  `bson:"segments" json:"segments"`
}

const (
	evServeAddr = "SERVE_ADDRESS"
	evMongoURL  = "MONGO_URL"
	evMongoDB   = "MONGO_DB"
	evMongoC    = "MONGO_COLLECTION"

	paramGID      = "group-id"
	paramUnit     = "unit"
	paramNsName   = "namespace-name"
	paramSegments = "namespace-segments"
	paramExpName  = "experiment-name"
	paramExpSeg   = "experiment-segments"
	paramExpDef   = "experiment-definition"
)

func init() {
	http.HandleFunc("/", rootHandler)
	http.HandleFunc("/namespace", namespaceHandler)
	http.HandleFunc("/experiment", experimentHandler)
}

func main() {
	// TODO: start health and liveliness server

	// setup config
	log.SetOutput(os.Stdout)
	if os.Getenv(evMongoURL) == "" {
		log.Fatal("must set MONGO_URL")
	}
	cfg.dbURL = os.Getenv(evMongoURL)

	if os.Getenv(evMongoDB) == "" {
		log.Fatal("must set MONGO_DB")
	}
	cfg.db = os.Getenv(evMongoDB)

	if os.Getenv(evMongoC) == "" {
		log.Fatal("must set MONGO_COLLECTION")
	}
	cfg.coll = os.Getenv(evMongoC)

	if os.Getenv(evServeAddr) == "" {
		log.Fatal("must set SERVE_ADDRESS")
	}
	cfg.addr = os.Getenv(evServeAddr)

	sess, err := mgo.Dial(cfg.dbURL)
	if err != nil {
		log.Fatalf("dialing mongodb: %v", err)
	}
	cfg.session = sess
	defer func() {
		cfg.session.Close()
	}()

	errChan := make(chan error)
	go func() {
		errChan <- http.ListenAndServe(cfg.addr, nil)
	}()

	signalChan := make(chan os.Signal, 1)
	signal.Notify(signalChan, syscall.SIGINT, syscall.SIGTERM)

	select {
	case err := <-errChan:
		if err != nil {
			log.Fatal(err)
		}
		// smooth shutdown
	case sig := <-signalChan:
		log.Println(fmt.Sprintf("Captured %v. Exitting...", sig))
		// smooth shutdown
		os.Exit(0)
	}
}

func checkParams(vals url.Values, keys []string) string {
	for _, k := range keys {
		if _, ok := vals[k]; !ok {
			return k
		}
	}
	return ""
}

func rootHandler(w http.ResponseWriter, r *http.Request) {
	var data []namespace
	c := cfg.session.DB(cfg.db).C(cfg.coll)
	namespaces := c.Find(bson.M{}).Iter()
	err := namespaces.All(&data)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	rootTmpl.Execute(w, data)
}

var rootTmpl = template.Must(template.ParseFiles("rootTemplate.html"))
