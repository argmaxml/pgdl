FROM postgres:16.2

COPY ./app /app

# Install dependencies for pgvector
RUN apt-get update && apt-get install --reinstall ca-certificates && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    python3 python3-pip \
    cron \
    postgresql-server-dev-16 \
    && rm -rf /var/lib/apt/lists/*

# Clone the pgvector repository and install it
RUN git clone https://github.com/pgvector/pgvector.git \
    && cd pgvector \
    && make \
    && make install

# Python requirements
RUN pip install --break-system-packages -r /app/requirements.txt && python3 /app/db.py

# Clean up
RUN apt-get purge -y --auto-remove build-essential git postgresql-server-dev-16 && rm -rf pgvector
