FROM python:3.12.3-bookworm

ARG POETRY_VERSION=1.8.3
ENV PYTHONUNBUFFERED=1
ENV POETRY_VIRTUALENVS_CREATE=false

RUN set -eux \
    && apt-get update && apt-get install -y --no-install-recommends \
      apt-transport-https \
      ca-certificates \
      curl \
      gnupg \
      jq \
      less \
      lsb-release \
      make \
      nginx \
      tree \
      vim \
      zip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry~=${POETRY_VERSION}

# TODO: Remove this once IntelliJ supports refresh Python packages in container.
COPY pyproject.toml poetry.lock /tmp/build/
WORKDIR /tmp/build
RUN poetry install \
    && rm -rf /tmp/build
