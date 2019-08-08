FROM python:3.6-slim
LABEL maintainer="Emmanuel Sackey"

COPY . /srv/flask_app
WORKDIR /srv/flask_app

# Install deps before we add our project to cache this layer
RUN apk add --no-cache gcc python-dev musl-dev libffi-dev openssl openssl-dev

#ADD . /app/

RUN pip install -r requirements.txt && \
    apk del gcc git python3-dev musl-dev libffi-dev openssl-dev && \
    pip install --upgrade pip

COPY nginx.conf /etc/nginx
RUN chmod +x ./start.sh
CMD ["./start.sh"]

ENTRYPOINT ["python3"]
CMD ["firefox_bpki.py"]