FROM python:3.11.5 as base

WORKDIR /usr/snapmsg-posts

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip

# Instala spaCy y descarga el modelo de lenguaje
RUN pip install spacy
RUN python -m spacy download en_core_web_sm

RUN pip install -r requirements.txt

COPY . .

# test stage
FROM base as test
RUN pip install pytest httpx
CMD pytest

# production stage
FROM base as prod
EXPOSE 3001
ENV DD_SERVICE=posts-ms
ENV DD_LOGS_INJECTION=true
ENV DD_ENV=prod

CMD ["ddtrace-run", "uvicorn", "src.main:app" ,"--host", "0.0.0.0", "--port", "3001"] 
