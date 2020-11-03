# Setup

## Getting the data into an Sqlite database

Use Docker to build and run each image as follows (replacing `<img_name>` with a name of your choice):

```bash
docker build -f cron/Dockerfile -t <img_name> .
docker run -itv `pwd`/data:/data <img_name>
```

This will build the image (if not already built) and start the download of the raw data (if not already done) into the `data` folder inside the current directory in the host, followed by the creation and population of a Sqlite database in the same directory.

## Get the "Hello World" Flask app running

As above, build and run the image using Docker like this:

```shell
docker build -t <img_name> .
docker run --name <container_name> -d -p 5000:5000 <img_name>
```
The app should be be available at http://localhost:5000/.