FROM python:3.8-alpine

WORKDIR /app
COPY requirements.txt .

RUN apk add --no-cache libheif-dev zlib-dev jpeg-dev gcc musl-dev
RUN pip3 install -r requirements.txt --no-binary :all:

COPY . .

ENTRYPOINT [ "python3", "main.py" ]