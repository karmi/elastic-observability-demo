#!/bin/bash

printenv | sed 's/^\(.*\)$/\1/g' > /app/.env

cron -f

# -----
# https://roboslang.blog/post/2017-12-06-cron-docker/#adding-system-variables
