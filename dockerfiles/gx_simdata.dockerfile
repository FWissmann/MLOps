FROM python:3.9
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install pandas numpy great_expectations pyarrow
CMD ["python", "gx_simdata.py"]
