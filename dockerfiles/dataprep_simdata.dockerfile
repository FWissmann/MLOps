FROM python:3.9
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install pandas numpy matplotlib seaborn
#ENV LANG en_US
#ENV LC_ALL en_US
#ENV LC_TIME en_US
CMD ["python", "dataprep_simdata.py"]
