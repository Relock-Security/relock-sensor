include .env

$(eval build:;@:)

certyficate:
	openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -sha256 -days 3650 -nodes -subj "/CN=$(HOST)" \
  		-addext "subjectAltName=DNS:$(HOST),DNS:*.$(HOST),IP:127.0.0.1"

image:
	docker build --no-cache -t relockid/sensor:latest -f docker/Dockerfile .

run:
	sudo docker run --name sensor \
					--user root \
					--privileged \
					--rm \
					 -v ./app:/demo/app \
					 -v ./main.py:/demo/main.py \
					 -v ./key.pem:/demo/key.pem \
					 -v ./cert.pem:/demo/cert.pem \
					 -v ./nginx/template.conf:/etc/nginx/sites-available/template.conf \
					--add-host=$(RELOCK_HOST):$(RELOCK_ADDR) \
					-it relockid/sensor run \
					--relock_host $(RELOCK_HOST) \
					--redis_host $(REDIS_HOST) \
					--host $(HOST) \
					--port 8080 \
					--ip 0.0.0.0 \
					--key key.pem \
					--crt cert.pem \
					--nginx \
					--debug 
