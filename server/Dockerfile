FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .

RUN pip3 install -r requirements.txt --extra-index-url https://www.piwheels.org/simple

COPY . .

ENTRYPOINT [ "python3", "main.py" ]