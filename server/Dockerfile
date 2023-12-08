FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .

RUN add-apt-repository ppa:strukturag/libheif
RUN apt update
RUN apt -y install libheif-dev
RUN pip3 install -r requirements.txt --no-binary :all:

COPY . .

ENTRYPOINT [ "python3", "main.py" ]