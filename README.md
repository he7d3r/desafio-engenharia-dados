
# Setup

## Quick start

After cloning the project, and going to its folder, use Docker Compose to build and run the images as follows:
```bash
docker-compose up -d
```

This will start both the cron job and the flask app. You can also start only the web app (e.g. if the data is already downloaded and added to the database, and you don't need the cron job running):

```bash
docker-compose up app -d
```

Alternatively, use Docker to build and run each image as follows:

## Get the data into an SQLite database

To get a container for the cron job, run the following (replacing `<img_name>` with a name of your choice):

```bash
docker build -f cron/Dockerfile -t <img_name> .
docker run -d -v `pwd`/data:/data <img_name>
```

This will build the image (if not already built) and start the periodical download of the raw data (if not already done) into the `data` folder inside the current directory in the host, followed by the creation and population of a SQLite database in the same directory.

You can check the status of the cron service like this:

```bash
docker exec -it <container_id> service cron status
```

## Get the Flask app running

As above, it is possible to build and run the image without using Docker Compose:

```shell
docker build -f dashboard/Dockerfile -t <img_name> .
docker run --name <container_name> -d -p 5000:5000 -v `pwd`/data:/data -v `pwd`/dashboard/src:/code/src <img_name>
```

The app should be be available at http://localhost:5000/. Changes made to app source code (inside the folder `dashboard/src` on the host) go live without needing to rebuild its image (reloading the page in the browser is enough).