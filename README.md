# STX Lunch
Aplikacja do zamawiania lunchy

# Requirements
* PostresSQL
* UWSGI

# Inicjalizacja

```shell
python3 bootstrap-buildout.py
./bin/buildout -vN
./bin/flask-ctl init_db --debug
ln -s /opt/python/3.4.2/bin/uwsgi uwsgi
```

# Uruchomienie

```shell
./bin/flask-ctl debug
```

lub

```shell
./bin/flask-ctl serve start
./bin/flask-ctl serve stop
./bin/flask-ctl serve restart
```

# Migrowanie

```shell
./bin/flask-ctl db_migrate init
./bin/flask-ctl db_migrate migrate
./bin/flask-ctl db_migrate upgrade
```