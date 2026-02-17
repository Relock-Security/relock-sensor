#
# PLEASE DO NOT EDIT IT DIRECTLY.
#

FROM ubuntu:latest

COPY docker/docker-entrypoint /usr/local/bin/
COPY nginx/template.conf /etc/nginx/sites-available/template.conf
COPY main.py /demo/main.py
COPY .env /demo/.env

ARG DEBIAN_FRONTEND=noninteractive

RUN set -eux; \
	\
	mkdir -p /demo && \
	chmod +x /usr/local/bin/docker-entrypoint;

RUN set -eux; \
	\
	apt-get update; \
	DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
		debconf ca-certificates gettext-base \
		nginx redis \
		python3 python3-pip python3-requests nano pkg-config \
		python3-dev default-libmysqlclient-dev build-essential \
		python3-async-timeout \
		python3-certifi \
		python3-cffi \
		python3-charset-normalizer \
		python3-click \
		python3-idna \
		python3-tomli \
		python3-ujson \
		python3-urllib3 \
		python3-xxhash \
		python3-dotenv \
		python3-flask \
		python3-flask-sqlalchemy \
		python3-flask-mail \
		python3-flask-compress \
		python3-flask-socketio \
		python3-flask-login \
		python3-werkzeug \
		python3-validators \
		python3-bleach \
		python3-redis ; \
	python3 -m pip install --upgrade --break-system-packages \
		Bootstrap-Flask Flask-Session; \
	apt-get remove -y python3-pip build-essential && apt-get clean; \
	rm -rf /var/lib/apt/lists/*;

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

VOLUME /data
WORKDIR /demo

EXPOSE 80 443 8111

ENTRYPOINT ["docker-entrypoint"]
CMD ["/bin/bash", "-c"]