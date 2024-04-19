FROM python:3.12

COPY requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

COPY ./scr /app

WORKDIR /app

CMD ["python", "main.py"]