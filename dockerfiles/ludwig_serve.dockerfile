FROM ludwigai/ludwig:latest
RUN pip install --upgrade pip
RUN pip install mlflow
WORKDIR /app
EXPOSE 8000
ENTRYPOINT [ "python" ]
CMD ["./ludwig_serve.py"]