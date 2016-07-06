# Copyright 2016 Nordstrom Inc., authors, and contributors <see AUTHORS file>
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
FROM python:2
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt

# TODO: eventually will want to run this as non root user
# RUN groupadd -r elwin && useradd -u 999 -r -g elwin x7qj
# USER x7qj
# WORKDIR /home/elwin
COPY elwin.py elwin.py
COPY experiments.py experiments.py
COPY storage.py storage.py

EXPOSE 5000
CMD ["/usr/local/bin/uwsgi", "--processes", "4", "--threads", "8", "--socket", "0.0.0.0:5000", "--wsgi-file", "/usr/src/app/elwin.py", "--callable", "app"]
