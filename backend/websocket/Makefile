DOCKER_COMPOSE_FILE=docker-compose.yml
APP_FOLDER=app/

test:
	python -m pytest tests/ -vv

linters:
	python -m black --line-length=79
	python -m flake8 --max-line-length=79
	python -m bandit -r $(APP_FOLDER) --skip "B101" --recursive
	python -m mypy --ignore-missing-imports $(APP_FOLDER)

run:
	docker-compose -f $(DOCKER_COMPOSE_FILE) up --build -d

stop:
	docker-compose -f $(DOCKER_COMPOSE_FILE) stop

deploy:
	python -m black --check --line-length=79 --exclude=tests/ $(APP_FOLDER)
	python -m flake8 --max-line-length=79 --exclude=tests/ $(APP_FOLDER)
	python -m bandit -r $(APP_FOLDER) --skip "B101" --recursive
	python -m mypy --ignore-missing-imports $(APP_FOLDER)
	python -m pytest tests/ -vv
	docker-compose -f $(DOCKER_COMPOSE_TEST_FILE) down

