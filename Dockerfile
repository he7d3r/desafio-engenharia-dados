FROM ubuntu:latest

# Install cron
RUN apt-get update && apt-get -y install cron make wget

# Create and set working directory
WORKDIR /code

# Copy the makefile to the working directory
COPY Makefile ./

# Add crontab file to the cron directory
COPY crontab /etc/cron.d/download-data

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/download-data

RUN cron

CMD ["/usr/bin/make", "all"]
