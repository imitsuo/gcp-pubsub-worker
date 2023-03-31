run:
	uvicorn app.main:app --reload

build:
	docker build -t gcp-pubsub-worker .
