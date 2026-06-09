REGISTRY = 192.168.0.69:30500
TAG = latest
SERVICE ?= service

.PHONY: build

build:
	docker buildx build \
		--platform linux/amd64,linux/arm64 \
		-t $(REGISTRY)/$(SERVICE):$(TAG) \
		--push \
		./$(SERVICE)
