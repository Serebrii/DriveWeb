FROM python:3.14-alpine

WORKDIR /app

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

COPY requirements.txt .

RUN pip install -r requirements.txt && \
    adduser --disabled-password --no-create-home django-user --gecos "" && \
    mkdir -p "/files/media/" && \
    chown -R django-user:django-user "/files/media/" && \
    chmod -R 755 "/files/media/"

COPY . .

USER django-user

CMD sh -c "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"
