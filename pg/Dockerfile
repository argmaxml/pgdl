FROM postgres:16.2

# Install dependencies for pgvector
RUN apt-get update && apt-get install --reinstall ca-certificates && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    postgresql-server-dev-16 \
    libcurl4-openssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Clone the pgvector repository and install it
RUN git clone https://github.com/pgvector/pgvector.git \
    && cd pgvector \
    && make \
    && make install

RUN git clone https://github.com/pramsey/pgsql-http.git \
    && cd pgsql-http \
    && make \
    && make install

# Clean up
RUN apt-get purge -y --auto-remove build-essential git postgresql-server-dev-16 \
    && rm -rf pgvector pgsql-http
