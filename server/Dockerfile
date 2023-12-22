FROM python:3.10-alpine

WORKDIR /app
COPY requirements.txt .

RUN apk add -u zlib-dev jpeg-dev gcc musl-dev
RUN pip3 install -r requirements.txt

COPY . .

ENTRYPOINT [ "python3", "main.py" ]