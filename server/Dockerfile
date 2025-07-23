FROM python:3.12

RUN apt-get update && \
    apt-get install -y --no-install-recommends --fix-missing \
        curl \
        libpq-dev \
        gcc \
        postgresql-client \
        make && \
    rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --shell /bin/bash app

WORKDIR /server
COPY . /server

RUN pip install --no-cache-dir -r requirements.txt

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN chown -R app:app /server

HEALTHCHECK CMD curl -f http://localhost:8000/health || exit 1

USER app

WORKDIR /

CMD ["/entrypoint.sh"]