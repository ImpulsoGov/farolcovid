IMAGE_TAG=impulsogov/simulacovid

UNAME := $(shell uname)
ifeq ($(UNAME), Linux)
SHELL := /bin/bash
else
SHELL := /bin/sh
endif

###
# Docker
###

# Build image
docker-build:
	docker build -t $(IMAGE_TAG) .

# Run just like the production environment
docker-run:
	docker run -d \
		--restart=unless-stopped \
		-v $(PWD)/.env:/home/ubuntu/.env:ro \
		-p 8501:8501 \
		$(IMAGE_TAG)

# Run development server with file binding from './src'
docker-dev:
	touch $(PWD)/.env
	docker run --rm -it \
		--name farolcovid-dev \
		-p 8501:8501 \
		-v $(PWD)/.env:/home/ubuntu/.env:ro \
		-v $(PWD)/src:/home/ubuntu/src:ro \
		$(IMAGE_TAG)

# Groups
docker-build-run: docker-build docker-run
docker-build-dev: docker-build docker-dev

# DEBUGING for production environment
docker-shell:
	docker run --rm -it \
		--entrypoint "/bin/bash" \
		-v $(PWD)/.env:/home/ubuntu/.env:ro \
		$(IMAGE_TAG)

# DEBUGING for staging environment
docker-heroku-test: docker-build
	docker run -it --rm \
		-e PORT=8080 \
		-p 8080:8080 \
		$(IMAGE_TAG)