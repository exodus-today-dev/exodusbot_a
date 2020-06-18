FROM python:3.7-slim-stretch

WORKDIR /app

RUN apt-get update

RUN apt-get -y install gcc

COPY requirements.txt /tmp

COPY . ./

RUN pip install -r /tmp/requirements.txt

VOLUME [ "/app" ]

EXPOSE 8443

CMD ["python3", "main.py"]
