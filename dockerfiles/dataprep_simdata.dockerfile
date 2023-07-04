FROM python:3.9
WORKDIR /app
RUN apt-get update && apt-get install -y locales && rm -rf /var/lib/apt/lists/* \
	&& localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8
RUN pip install --upgrade pip
RUN pip install pandas numpy matplotlib seaborn
CMD ["python", "dataprep_simdata.py"]
