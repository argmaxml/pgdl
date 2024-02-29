FROM python:3.11-slim
WORKDIR /usr/src/app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
RUN rm Dockerfile requirements.txt
RUN python3 create_test_data_table.py
RUN python3 db_model.py
EXPOSE 8080
ENV UVICORN_PORT=8080 UVICORN_HOST=0.0.0.0
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]
