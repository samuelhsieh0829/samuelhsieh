FROM python:3.11.10-slim

WORKDIR /app
ADD . /app
RUN pip install -r requirements.txt

CMD ["python", "main.py"]