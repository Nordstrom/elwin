package main

import (
	"encoding/base64"
	"encoding/json"
	"fmt"
	"math/rand"
	"net/http"
	"strconv"
	"strings"
	"time"

	"gopkg.in/mgo.v2/bson"
)

func init() {
	rand.Seed(time.Now().UTC().UnixNano())
}

func experimentHandler(w http.ResponseWriter, r *http.Request) {
	switch r.Method {
	case "GET":
		getExperiment(w, r)
	case "POST":
		setExperiment(w, r)
	case "DELETE":
		deleteExperiment(w, r)
	default:
		http.Error(w, "bad request method", http.StatusBadRequest)
	}
}

func getExperiment(w http.ResponseWriter, r *http.Request) {
	if err := r.ParseForm(); err != nil {
		http.Error(w, "error parsing data: "+err.Error(), http.StatusBadRequest)
		return
	}
	if badKey := checkParams(r.Form, []string{
		paramNsName,
		paramExpName,
	}); badKey != "" {
		http.Error(w, "missing param: "+badKey, http.StatusBadRequest)
		return
	}

	c := cfg.session.DB(cfg.db).C(cfg.coll)
	var doc namespace
	selector := bson.M{
		"name":             r.Form.Get(paramNsName),
		"experiments.name": r.Form.Get(paramExpName),
	}
	if err := c.Find(selector).One(&doc); err != nil {
		http.Error(w, "error finding experiment "+r.Form.Get(paramExpName)+": "+err.Error(), http.StatusInternalServerError)
		return
	}

	enc := json.NewEncoder(w)
	if err := enc.Encode(doc); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
}

func setExperiment(w http.ResponseWriter, r *http.Request) {
	if err := r.ParseForm(); err != nil {
		http.Error(w, "error parsing data: "+err.Error(), http.StatusBadRequest)
		return
	}
	if badKey := checkParams(r.Form, []string{
		paramNsName,
		paramExpName,
		paramExpSeg,
		paramExpDef,
	}); badKey != "" {
		http.Error(w, "missing param: "+badKey, http.StatusBadRequest)
		return
	}

	c := cfg.session.DB(cfg.db).C(cfg.coll)
	var doc namespace
	selector := namespace{Name: r.Form.Get(paramNsName)}
	if err := c.Find(selector).One(&doc); err != nil {
		http.Error(w, "error finding namespace "+r.Form.Get(paramNsName)+": "+err.Error(), http.StatusInternalServerError)
		return
	}

	numSeg, err := strconv.Atoi(r.Form.Get(paramExpSeg))
	if err != nil {
		http.Error(w, "parsing segments: "+err.Error(), http.StatusBadRequest)
		return
	}
	if len(doc.AvailableSegments) < numSeg {
		err := fmt.Sprintf("not enough segments: want %v got %v", numSeg, len(doc.AvailableSegments))
		http.Error(w, err, http.StatusBadRequest)
		return
	}
	_, expSeg := sample(doc.AvailableSegments, numSeg)

	br := base64.NewDecoder(base64.StdEncoding, strings.NewReader(r.Form.Get(paramExpDef)))
	dec := json.NewDecoder(br)
	var def map[string]interface{}
	if err := dec.Decode(&def); err != nil {
		http.Error(w, "error decoding definition: "+err.Error(), http.StatusBadRequest)
		return
	}

	err = c.Update(selector, bson.M{
		"$push": bson.M{
			"experiments": bson.M{
				"name":       r.Form.Get(paramExpName),
				"segments":   expSeg,
				"definition": def,
			},
		},
	})

	if err != nil {
		http.Error(w, "error adding experiment: "+err.Error(), http.StatusInternalServerError)
		return
	}

	if err := c.Update(selector, bson.M{
		"$pullAll": bson.M{
			"available_segments": expSeg,
		},
	}); err != nil {
		http.Error(w, "error updating available segments: "+err.Error(), http.StatusInternalServerError)
		return
	}
}

func sample(src []int, n int) (orig, sample []int) {
	out := make([]int, n)
	for i := range out {
		ii := rand.Intn(len(src))
		out[i] = src[ii]
		src = append(src[:ii], src[ii+1:]...)
	}

	return src, out
}

func deleteExperiment(w http.ResponseWriter, r *http.Request) {
	if err := r.ParseForm(); err != nil {
		http.Error(w, "error parsing data: "+err.Error(), http.StatusBadRequest)
		return
	}
	if badKey := checkParams(r.Form, []string{
		paramNsName,
		paramExpName,
	}); badKey != "" {
		http.Error(w, "missing param: "+badKey, http.StatusBadRequest)
		return
	}

	c := cfg.session.DB(cfg.db).C(cfg.coll)
	var ns namespace
	if err := c.Find(bson.M{
		"name":             r.Form.Get(paramNsName),
		"experiments.name": r.Form.Get(paramExpName),
	}).One(&ns); err != nil {
		http.Error(w, "error finding experiment: "+err.Error(), http.StatusBadRequest)
		return
	}
	var segments []int
	for _, e := range ns.Experiments {
		if e.Name != r.Form.Get(paramExpName) {
			continue
		}
		segments = e.Segments
		break
	}

	if err := c.Update(bson.M{
		"name": r.Form.Get(paramNsName),
	}, bson.M{
		"$pushAll": bson.M{
			"available_segments": segments,
		},
		"$pull": bson.M{
			"experiments": bson.M{"name": r.Form.Get(paramExpName)},
		},
	}); err != nil {
		http.Error(w, "error removing experiment: "+err.Error(), http.StatusInternalServerError)
		return
	}
}
