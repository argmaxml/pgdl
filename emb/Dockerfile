FROM python:3.11-slim
WORKDIR /usr/src/app
COPY . .
RUN pip install -r requirements.txt # --no-cache-dir after install
EXPOSE 8080
ENV UVICORN_PORT=8080 UVICORN_HOST=0.0.0.0

CMD ["bash", "run.sh"]
