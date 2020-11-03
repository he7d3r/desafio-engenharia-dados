
# Setup

## Getting the data into an Sqlite database

On linux, use Docker to build and run the image as follows (replacing `cron-downloader` with a name of your choice):

```bash
$ docker build -f cron/Dockerfile -t cron-downloader .
Sending build context to Docker daemon  2.329GB
Step 1/13 : FROM python:3
...
Successfully tagged cron-downloader:latest
$ docker run -itv `pwd`/data:/data cron-downloader
wget -P data -Nc "http://www.mdic.gov.br/balanca/bd/comexstat-bd/ncm/IMP_2017.csv"
...
all success
```

This will build the image (if not already built) and start the download of the raw data (if not already done) into the folder `data` inside the current directory in the host.

## Creating a "hello world" Flask app for the dashboard

```shell
docker build -t dashboard-app:latest .
docker run --name my-dashboard-app -d -p 5000:5000 dashboard-app
```
