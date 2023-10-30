## posts API 1.0.0
## 
PORT=3001

.PHONY: clean test run-local

help:        ## Show this help.
	@sed -ne '/@sed/!s/## //p' $(MAKEFILE_LIST)

run-local:   ## Run locally
	uvicorn src.main:app --host 0.0.0.0 --port ${PORT} --reload

build: clean ## Build the docker image
	docker build -t posts-ms --target prod .

run: build   ## Run the docker image (and build)
	docker run --rm --name posts-ms -p ${PORT}:3001 posts-ms:latest

test:        ## Run dockerized tests
	docker build -t posts-ms-test --target test .
	- docker run --tty --name posts-ms-test posts-ms-test:latest pytest -v
	- @docker container rm -f posts-ms-test > /dev/null 2>&1
	- @docker image rm -f posts-ms-test > /dev/null 2>&1

format:      ## Format (yapf must be installed)
	yapf -i --style google src/*.py test/*.py
	
clean:       ## Remove image 
	docker image rm -f posts-ms

compose:  ## Stop services, remove containers, and start services again
	- docker compose -f docker-compose-local.yml down --remove-orphans 
	- docker rmi posts-ms
	docker compose -f docker-compose-local.yml up --build  

