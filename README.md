# csrgenerator.com
[![Build Status](https://github.com/davidwittman/csrgenerator.com/actions/workflows/python-app.yml/badge.svg)](https://github.com/davidwittman/csrgenerator.com/actions/workflows/python-app.yml/badge.svg) [![Docker Hub](https://img.shields.io/docker/automated/wittman/csrgenerator.com.svg)](https://hub.docker.com/r/wittman/csrgenerator.com/)

This is the public repository for https://csrgenerator.com. It's a pretty simple Flask webapp which generates a Certificate Signing Request for creating SSL certificates. Sure, you can do it with OpenSSL via the command-line, but not everyone is as smart as you are.

## Running with Docker

``` bash
$ docker run -d -p 8080:8080 --name csrgenerator wittman/csrgenerator.com
```
