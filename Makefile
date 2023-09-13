
.PHONY: clean

run-local:
	uvicorn src.main:app --host 0.0.0.0 --port 3000 --reload

run: clean 
	docker compose up

clean: 
	docker compose down
	docker image rm -f users-ms
	docker container rm -f users-ms
