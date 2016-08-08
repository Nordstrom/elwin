# elwin

Checkout [choices][choices] our simpler/faster impementation.

Elwin is [planout][planout] as a service. It provides an easy way to run many
concurrent experiments.

```bash
# for example if you were running a single color test that hashed on userid
$ curl "elwin.example.com/?group-id=team-name&userid=123456789"
{
  experiments: {
    colorTest: {
      color: "#000000"
    }
  }
}
```

`group-id` is a tag on the [namespace][ns]. It determines which tests are
returned. Only namespaces that have a matching `group-id` will be returned.

`userid` is an input to the experiment. All experiments have a [unit][unit]
used to hash users. Namespaces operate over a unit or set of units to hash
users into experiments. These same units are also inputs into the experiment.
Experiments must have the same units as their namespace.

## Running in docker

The easiest way to get started is using the prebuilt docker images.

``` bash
# run mongo db
docker run -d \
  --name mdb \
  mongo

# load example data
docker run -d \
 --link mdb:elwin-storage \
 foolusion/elwin-test

# run elwin
docker run -d \
  -p 5000:5000 \
  --link mdb:elwin-storage \
  foolusion/elwin
curl "localhost:5000/?group-id=epe&userid=12345789"
```

## Running in virtualenv

If you want to build from scratch.

``` bash
git clone https://github.com/nordstrom/elwin.git
cd elwin
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
DB_CONN=mongodb://your-mongo-database:27017 venv/bin/gunicorn myapp:application
```

Elwin is a [philologist](https://en.wikipedia.org/wiki/Philology).

[choices]: https://github.com/foolusion/choices
[planout]: http://facebook.github.io/planout
[ns]: http://facebook.github.io/planout/docs/namespaces.html
[unit]: http://facebook.github.io/planout/docs/planout-language-reference.html#planout-syntax-and-operators
