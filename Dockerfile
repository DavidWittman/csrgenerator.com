FROM jazzdd/alpine-flask:python3
LABEL maintainer="David Wittman"

# Install deps before we add our project to cache this layer
RUN apk add --no-cache gcc python3-dev musl-dev libffi-dev openssl openssl-dev

ADD . /app/

RUN pip install -r requirements.txt && \
    apk del gcc git python3-dev musl-dev libffi-dev openssl-dev
