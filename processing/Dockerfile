FROM python:3.8-buster

COPY requirements.txt /app/
WORKDIR /app

RUN pip install --upgrade pip \
    &&  pip install --trusted-host pypi.python.org --requirement requirements.txt

CMD ["python", "main.py"]