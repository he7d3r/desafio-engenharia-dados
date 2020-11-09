FROM python:3

# Install some packages
RUN apt-get update \
    && apt-get -y install cron make wget

# Create and set working directory
WORKDIR /code

# Copy the makefile to the working directory
COPY cron/Makefile ./
# FIXME: Copy only the needed script (add others later)
COPY cron/scripts ./scripts
RUN chmod +x ./scripts/*.py

# Install python packages
COPY cron/requirements.txt ./
RUN pip install -r requirements.txt

# Add crontab file to the cron directory
COPY cron/crontab /etc/cron.d/download-data

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/download-data

# Script for cron. See https://unix.stackexchange.com/a/453053/33604
RUN chmod +x ./scripts/entrypoint.sh
ENTRYPOINT ["/code/scripts/entrypoint.sh"]

CMD /usr/bin/make all \
    # Create the log file which tail will follow
    && touch /var/log/download-data.log \
    # Monitor the cron job
    && tail -f /var/log/download-data.log
