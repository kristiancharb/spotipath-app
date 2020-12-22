#!/bin/bash

git pull

# Stop prod service
docker-compose -f docker-compose.prod.yml down -v

# Rebuild prod service and restart
docker-compose -f docker-compose.prod.yml up -d --build

# Import DB dump 
zcat ~/spotify_dump.gz | psql -h 127.0.0.1 --username=postgres --dbname=spotify