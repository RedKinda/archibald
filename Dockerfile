FROM alpine

WORKDIR /var/www

RUN apk add --update build-base g++ git make libcap-dev cargo
RUN git clone https://github.com/ioi/isolate && \
    cd isolate && \
    make install && \
    isolate --init

COPY start.sh ./
COPY ./src ./archibald/src
COPY ./Cargo.toml ./archibald/

RUN cd /var/www/archibald && \
    cargo build --release

#CMD sleep 99999999
# ENTRYPOINT ["sh"]
ENTRYPOINT ["/var/www/archibald/target/release/archibald"]