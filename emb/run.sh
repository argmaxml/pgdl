#!/bin/bash
sleep 5;python3 db_model.py;sleep 2;uvicorn api:app --host 0.0.0.0 --port 8080
