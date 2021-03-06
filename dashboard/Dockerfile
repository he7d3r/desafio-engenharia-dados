FROM python:3

# Install some packages
RUN apt-get update \
    && apt-get -y install cron

# Create and set working directory
WORKDIR /dashboard

# Install python packages
COPY dashboard/requirements.txt ./
RUN pip install -r requirements.txt

# Add crontab file to the cron directory
COPY dashboard/crontab /etc/cron.d/download-data

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/download-data

# Script for cron. See https://unix.stackexchange.com/a/453053/33604
COPY dashboard/entrypoint.sh ./
RUN chmod +x ./entrypoint.sh

# Copy the makefile to the working directory
COPY dashboard/Makefile ./

# Copy the dashboard source to the working directory
COPY dashboard/src/ ./src/
COPY dashboard/wsgi.py ./

# Run the image as a non-root user
RUN useradd -m dashboarduser
USER dashboarduser

# TODO: Restore cron job
# ENTRYPOINT ["/dashboard/entrypoint.sh"]
CMD gunicorn --bind 0.0.0.0:$PORT "wsgi:app"