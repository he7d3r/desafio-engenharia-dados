
# Setup

## Quick start

### Using Docker Compose

After cloning the project, and going to its folder, use Docker Compose to build and run the images as follows:

```bash
docker-compose up -d
```

This should take care of building the images and running the following services:

- **cron-downloader**:
  - Download the raw data (if not already done) into the `data` folder
  - Create and populate a SQLite database in the same directory
  - Do a sanity test of the data
  - Start a cron job for downloads
- **app** + **nginx**: Make the dashboard app available at http://localhost:80, and at URLs such as http://localhost/dashboard/SC/2019, where "SC" and "2019" can be replaced by other state codes and years respectively.

In case the data is already downloaded, added to the database, and you don't need the cron job running, it is enough to run the following to have access to the dashboard:

```bash
docker-compose up -d nginx
```

### Other useful commands

#### Debugging

You can enable Flask's debug mode by setting a environment variable like this:

```bash
FLASK_ENV=development docker-compose up -d app
```

or by adding the same setting to a `.env` file:

```bash
echo "FLASK_ENV=development" >> .env
```

To disable it again, set `FLASK_ENV` to `production` instead of `development`.

#### Get the data into an SQLite database

To get a container for the downloader, run the following (replacing `<img_name>` with a name of your choice):

```bash
docker build -f cron/Dockerfile -t <img_name> .
docker run -d -e DATABASE_URL='sqlite:////data/trades.db' \
    -v `pwd`/data:/data <img_name>
```

#### Check the cron service status

You can check the status of the cron service like this:

```bash
docker exec -it <container_id> service cron status
```

#### Test the database

After making changes to the data pipeline, it can be useful to check if the database still contains the expected data. For this, just run `make tests` inside the `cron` container, that is:

```bash
docker-compose up -d cron-downloader
docker exec -it cron make tests
```

This will ensure a reasonable number of rows is present in each table.

#### Get the Flask app running

To build and run the app image:

```shell
docker build -f dashboard/Dockerfile -t <img_name> .
docker run -d -e FLASK_APP='src/app.py' \
    -e FLASK_ENV='development' \
    -e DATABASE_URL='sqlite:////data/trades.db' \
    -p 5000:5000 \
    -v `pwd`/data:/data \
    -v `pwd`/dashboard/src:/code/src \
    --name <container_name> <img_name> \
    gunicorn --reload --bind 0.0.0.0:5000 --workers 4 "src.app:create_app()"
```

In this example, the app should be be available at http://localhost:5000/. If needed, add the option `--reload` to allow changes made to app source code (inside the folder `dashboard/src` on the host) to go live without needing to rebuild its image (reloading the page in the browser will be enough).

## Notes

For a first look into the data, check out the Jupyter notebooks inside the directory `notebooks`.

## Database Layout

Currently, the database tables are organized as follows:

![Database Diagram](diagram.png)
