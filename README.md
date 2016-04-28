# elwin
Elwin is a [philologist](https://en.wikipedia.org/wiki/Philology).

## Running in docker

``` bash
docker run -d \
  --name mdb \
  mongo

docker run -d \
  -p 5000:5000 \
  --link mdb:elwin-storage \
  foolusion/elwin
```

## Running in virtualenv

``` bash
git clone https://github.com/nordstrom/elwin.git
cd elwin
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
DB_CONN=mongodb://your-mongo-database:27017 venv/bin/gunicorn myapp:application
```
