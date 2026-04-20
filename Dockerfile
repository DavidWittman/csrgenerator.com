FROM python:3.14-slim
LABEL maintainer="David Wittman"
EXPOSE 8080
WORKDIR /www
COPY . /www/
RUN pip install --no-cache-dir gunicorn && \
    pip install --no-cache-dir -r requirements.txt
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--access-logfile", "-", "app:app"]
