#!/bin/bash

# Command 1
command1="python3 db_model.py"

# Command 2
command2="uvicorn api:app --host 0.0.0.0 --port 8080"

# Run the commands
sleep 5
$command1
$command2