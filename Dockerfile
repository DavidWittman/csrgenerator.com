FROM jazzdd/alpine-flask:python3
LABEL maintainer="David Wittman"

RUN apk add --no-cache \
        gcc \
        python3-dev \
        musl-dev \
        libffi-dev \
        openssl \
        openssl-dev

ADD . /app/

RUN export CRYPTOGRAPHY_DONT_BUILD_RUST=1 && \
    pip install -r requirements.txt && \
    apk del gcc git python3-dev musl-dev libffi-dev openssl-dev
