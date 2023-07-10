FROM python:3.11
WORKDIR /app
RUN apt-get update && apt-get install -y locales && rm -rf /var/lib/apt/lists/* \
	&& localedef -i de_DE -c -f UTF-8 -A /usr/share/locale/locale.alias de_DE.UTF-8
RUN pip install --upgrade pip
RUN pip install pandas==1.5.3 numpy matplotlib seaborn scikit-learn
CMD ["python", "dataprep_realdata.py"]
