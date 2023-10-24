FROM python:3.9

WORKDIR /usr/snapmsg-posts

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

COPY . .

EXPOSE 3001

#ENV NEW_RELIC_CONFIG_FILE=/usr/snapmsg-users/newrelic.ini

#CMD ["newrelic-admin", "run-program", "uvicorn", "src.main:app" ,"--host", "0.0.0.0", "--port", "3001"] 
CMD ["ddtrace-run", "uvicorn", "src.main:app" ,"--host", "0.0.0.0", "--port", "3001"] 
