#!/bin/bash
# Wait for the Postgres server to be available
# You can include logic here to wait for the database to be ready

# Execute the SQL script
psql -U $POSTGRES_USER -h $POSTGRES_HOST -d $POSTGRES_DB -a -f /app/dump.sql
