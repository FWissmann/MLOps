import requests
import time
import os
import mlflow
import subprocess
from datetime import datetime

# Logging
def get_currentTimeMicro():
    return (f'<{datetime.now().strftime("%H:%M:%S.%f")}> ')
gctm = get_currentTimeMicro

# Check if run on Docker or locally
def is_running_in_docker():
    return os.path.exists('/.dockerenv')
if is_running_in_docker():
    print(f'{gctm()}Main thread: Running in Docker')
    run_in_docker  = True
else:
    print(f'{gctm()}Main thread: Running locally')
    run_in_docker = False

print(f'{gctm()}Main thread: Setting URLs ...')
# The REST API endpoint
if run_in_docker:
    url = "http://172.17.0.7:5000/api/2.0/mlflow/"
else:
    url = "http://213.136.77.216:5000/api/2.0/mlflow/"

# MLFlow Tracking URI
if run_in_docker:
    mlflow_uri = "http://172.17.0.7:5000"
else:
    mlflow_uri = "http://213.136.77.216:5000/"
mlflow.set_tracking_uri(mlflow_uri)

# LudwigAI command
print(f'{gctm()}Main thread: Setting LudwigAI serve command ...')
ludwig_serve_command = f'ludwig serve -m ./model/model/'
#ludwig_serve_command = f'ping 8.8.8.8 -t'
lsc_split = ludwig_serve_command.split()

# Get current run name
print(f'{gctm()}Main thread: Getting current run name ...')
response_json_model = (requests.get(url + "registered-models/get-latest-versions?name=Generator&stages=Production")).json()
current_run = response_json_model["model_versions"][0]["source"]

# Download model
print(f'{gctm()}Main thread: Downloading model ...')
mlflow.artifacts.download_artifacts(artifact_uri = current_run, dst_path="./")

# Start LudwigAI serve with downloaded model
print(f'{gctm()}Main thread: Starting LudwigAI serve ...')
ludwig_serve= subprocess.Popen(lsc_split, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
print(f'{gctm()}Main thread: LudwigAI serve started')

while True:
    # Make a GET request to the REST API
    print(f'{gctm()}Main thread: Checking for new model ...')
    response_json_model = (requests.get(url + "registered-models/get-latest-versions?name=Generator&stages=Production")).json()

    if response_json_model["model_versions"][0]["source"] != current_run:
        print(f'{gctm()}Main thread: New model found, downloading ...')
        current_run = response_json_model["model_versions"][0]["source"]
        mlflow.artifacts.download_artifacts(artifact_uri = current_run, dst_path="./")
        print(f'{gctm()}Main thread: New model downloaded, restarting LudwigAI serve ...')
        ludwig_serve.kill()
        ludwig_serve= subprocess.Popen(lsc_split, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        print(f'{gctm()}Main thread: LudwigAI serve restarted')
    print(f'{gctm()}Main thread: Waiting for 60 seconds ...')
    time.sleep(60)