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
	"encoding/json"
	"net/http"
	"strconv"

	"gopkg.in/mgo.v2/bson"
)

func namespaceHandler(w http.ResponseWriter, r *http.Request) {
	switch r.Method {
	case "GET":
		getNamespace(w, r)
	case "POST":
		setNamespace(w, r)
	case "DELETE":
		deleteNamespace(w, r)
	default:
		http.Error(w, "bad request method", http.StatusBadRequest)
	}
}

func getNamespace(w http.ResponseWriter, r *http.Request) {
	if err := r.ParseForm(); err != nil {
		http.Error(w, "error parsing data: "+err.Error(), http.StatusBadRequest)
		return
	}
	if badKey := checkParams(r.Form, []string{
		paramGID,
		paramUnit,
	}); badKey != "" {
		http.Error(w, "missing param: "+badKey, http.StatusBadRequest)
		return
	}

	var data []namespace
	c := cfg.session.DB(cfg.db).C(cfg.coll)
	namespaces := c.Find(bson.M{"group_ids": r.Form.Get(paramGID), "units": r.Form[paramUnit]}).Iter()
	err := namespaces.All(&data)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	enc := json.NewEncoder(w)
	if err := enc.Encode(data); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
}

func setNamespace(w http.ResponseWriter, r *http.Request) {
	if err := r.ParseForm(); err != nil {
		http.Error(w, `could not parse query params or form data`, http.StatusBadRequest)
		return
	}
	if badKey := checkParams(r.Form, []string{
		paramGID,
		paramNsName,
		paramUnit,
		paramSegments,
	}); badKey != "" {
		http.Error(w, "missing param: "+badKey, http.StatusBadRequest)
		return
	}
	var segments int
	if seg := r.Form.Get(paramSegments); seg != "" {
		i, err := strconv.Atoi(seg)
		if err != nil {
			http.Error(w, "error converting segments to int: "+err.Error(), http.StatusBadRequest)
			return
		}
		segments = i
	} else {
		segments = 1000
	}

	avail := make([]int, segments)
	for i := range avail {
		avail[i] = i + 1
	}

	c := cfg.session.DB(cfg.db).C(cfg.coll)
	err := c.Insert(&namespace{
		Name:              r.Form.Get(paramNsName),
		GroupIDs:          r.Form[paramGID],
		Units:             r.Form[paramUnit],
		NumSegments:       segments,
		AvailableSegments: avail,
		Experiments:       []experiment{},
	})
	if err != nil {
		http.Error(w, "error inserting to db: "+err.Error(), http.StatusInternalServerError)
		return
	}
}

func deleteNamespace(w http.ResponseWriter, r *http.Request) {
	if err := r.ParseForm(); err != nil {
		http.Error(w, `could not parse query params or form data`, http.StatusBadRequest)
		return
	}
	if badKey := checkParams(r.Form, []string{paramNsName}); badKey != "" {
		http.Error(w, "missing param: "+badKey, http.StatusBadRequest)
		return
	}
	c := cfg.session.DB(cfg.db).C(cfg.coll)
	if err := c.Remove(bson.M{"name": r.Form.Get(paramNsName)}); err != nil {
		http.Error(w, "error deleting document: "+err.Error(), http.StatusInternalServerError)
		return
	}
}
