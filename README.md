# Remote File System

## Pre-requisites
The dependencies for the Remote File System in Python must be installed via Poetry or pip. 

### Installing dependencies via Poetry
Follow the guide to install Poetry [here](https://python-poetry.org/docs/#installation).

Install the dependencies with Poetry:
```shell
poetry install
```

### Installing dependencies via pip
```shell
pip install -r requirements.txt
```

## Getting started
To start the server, run:
```shell
./remote_file_system/server_startup.py -i 0 -sip 127.0.0.1 -sp 12345 -dir server_dir
```

To start a client, run:
```shell
./remote_file_system/client_startup.py -cp 15000 -sip 127.0.0.1 -sp 12345 -c client1
```
