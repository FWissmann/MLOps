FROM python:3.9
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install pandas numpy matplotlib seaborn
CMD ["python", "prep_simdata.py"]
