# Build stage
FROM python:3.10.4-slim-buster

RUN pip install kafka-python flask

COPY ./events.py ./

CMD ["python", "-u", "./events.py"]