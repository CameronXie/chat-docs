FROM ollama/ollama:latest

RUN set -eux \
    && apt-get update && apt-get install -y --no-install-recommends \
      apt-transport-https \
      ca-certificates \
      curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY ./start.sh /deployment/
RUN	chmod +x /deployment/start.sh

STOPSIGNAL SIGTERM
ENTRYPOINT []
CMD /deployment/start.sh
