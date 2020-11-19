#!/bin/sh
set -e

# Reduce the hardlink count to 1. See https://unix.stackexchange.com/a/453053/33604
touch /etc/crontab /etc/cron.*/*

# Start the data download job
service cron start

# Run the CMD
exec "$@"