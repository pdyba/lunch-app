# STX Lunch
Lunch ordering application.

# Requirements
* PostresSQL
* uWSGI

# Install

```shell
python3 bootstrap-buildout.py
./bin/buildout -vN
ln -s /opt/python/3.4.2/bin/uwsgi uwsgi
```

## DB initialization

#### dev instance
```shell
./bin/flask-ctl init_db --debug
./bin/flask-ctl db_migrate stamp --debug
```

#### prod instance
```shell
./bin/flask-ctl init_db
./bin/flask-ctl db_migrate stamp
```

# Running

#### dev instance
```shell
./bin/flask-ctl debug
```

#### prod instance
```shell
./bin/flask-ctl serve start
./bin/flask-ctl serve stop
./bin/flask-ctl serve restart
```

# Update

## DB migrate

#### dev instance
```shell
./bin/flask-ctl db_migrate upgrade --debug
```

#### prod instance
```shell
./bin/flask-ctl db_migrate upgrade
```