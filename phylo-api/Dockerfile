FROM python:3.10
WORKDIR /app/

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT gunicorn --workers=1 --bind=0.0.0.0:2507 main:app
EXPOSE 2507
