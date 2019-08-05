FROM jazzdd/alpine-flask:latest
LABEL maintainer="Emmanuel Sackey"

# Install deps before we add our project to cache this layer
RUN apk add --no-cache gcc python-dev musl-dev libffi-dev openssl openssl-dev

ADD . /app/

RUN pip install -r requirements.txt && \
    apk del gcc git python3-dev musl-dev libffi-dev openssl-dev && \
    pip install --upgrade pip

ENTRYPOINT ["python3"]
CMD ["bpki.py"]


