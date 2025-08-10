# Build stage
FROM python:3.10.4-slim-buster

RUN pip install requests flask

COPY ./proxy.py ./

CMD ["python", "-u", "./proxy.py"]