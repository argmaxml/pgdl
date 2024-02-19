# pgdl

docker pull postgres:latest
docker run --name pgvector -e POSTGRES_PASSWORD=<your_password> -d -p 5432:5432 postgres
docker exec -it pgvector bash
docker exec -it pgvector psql -U postgres
CREATE EXTENSION vector;
