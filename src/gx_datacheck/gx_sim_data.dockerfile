FROM python:3.9
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install pandas numpy great_expectations pyarrow
COPY . /app/
CMD ["python", "gx_sim_data.py"]
