FROM postgres

WORKDIR /app/db

COPY dump.sql dump.sql
COPY init.sh init.sh

RUN chmod +x /app/db/init.sh

# Set the script to run when the container starts
ENTRYPOINT ["/app/db/init.sh"]
