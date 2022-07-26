FROM python:3.10
WORKDIR /app/

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT gunicorn --workers=4 --bind=0.0.0.0:2506 wsgi:app
EXPOSE 2506
