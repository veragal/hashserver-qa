FROM alpine:3.15.0 as base

RUN apk add --update --no-cache \
        wget \
        binutils \
        build-base \
        gcompat \
        musl-dev \
    && rm -rf /var/cache/apk/*

RUN wget --no-check-certificate --no-proxy \
        https://qa-broken-hashserve-jc.s3.amazonaws.com/broken-hashserve.tar \
    && tar -xf broken-hashserve.tar

ENV PORT=8888
