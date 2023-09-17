# Get the parent directory name
PARENT_FOLDER_NAME := $(shell basename "$(shell dirname "$(CURDIR)")")

.PHONY: build run watch link

build:
	@PROJECT_NAME=$(PARENT_FOLDER_NAME) docker-compose build --no-cache

run:
	@PROJECT_NAME=$(PARENT_FOLDER_NAME) docker-compose up

watch:
	docker exec -it $(PARENT_FOLDER_NAME)-service sh -c "cd webapp && npm run dev:watch"

link:
	docker exec -it $(PARENT_FOLDER_NAME)-service sh -c "cd webapp && ./link_mephisto_task.sh"