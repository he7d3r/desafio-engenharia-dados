
# Setup


## Quick start
On linux, use Docker Compose to build and run the images as follows:
```bash
docker-compose up -d
```

This will start both the cron job and the flask app.

## Getting the data into an Sqlite database

Alternatively, use Docker to build and run each image as follows (replacing `<img_name>` with a name of your choice):

```bash
docker build -f cron/Dockerfile -t <img_name> .
docker run -itv `pwd`/data:/data <img_name>
```

This will build the image (if not already built) and start the periodical download of the raw data (if not already done) into the `data` folder inside the current directory in the host, followed by the creation and population of a Sqlite database in the same directory

## Get the "Hello World" Flask app running

As above, it is possible to build and run the image without using Docker Compose:

```shell
docker build -t <img_name> .
docker run --name <container_name> -d -p 5000:5000 <img_name>
```
The app should be be available at http://localhost:5000/.