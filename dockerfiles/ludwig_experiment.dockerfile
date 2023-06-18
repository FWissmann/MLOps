FROM ludwigai/ludwig:latest
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install mlflow