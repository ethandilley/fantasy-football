REGISTRY = 192.168.0.69:30500
TAG = latest
SERVICE ?= service

.PHONY: up airflow build

up:
	docker compose -f compose.airflow.yaml -f compose.yaml up

airflow:
	helm upgrade --install airflow apache-airflow/airflow -f infra/airflow.yaml

build:
	docker buildx build \
		--platform linux/amd64,linux/arm64 \
		-t $(REGISTRY)/$(SERVICE):$(TAG) \
		--push \
		./$(SERVICE)
