POETRY = ./.venv/bin/poetry


venv:
	@rm -rf .venv || true && \
	python3.11 -m venv .venv && \
	.venv/bin/pip install poetry && \
	${POETRY} install --no-root


# WhatchTogether
run_dev:
	docker compose -f docker-compose.dev.yaml up -d

stop_dev:
	docker compose -f docker-compose.dev.yaml down -v

build:
	docker build -t watch_together_service -f ./docker/Dockerfile .

build_dev:
	docker build -t watch_together_service-dev -f ./docker/Dockerfile.test .

run_with_uvicorn:
	uvicorn --app-dir ./watch_together/app main:app --host=0.0.0.0 --port=8080 --reload --log-config=./watch_together/app/log_conf.yaml

local_tests:
	poetry run pytest -vx ./tests

local_flake8:
	poetry run flake8 watch_together/app

local_black:
	poetry run black watch_together/app

# Auth
build_auth_image:
	docker build -t auth-service -f auth_service/docker/Dockerfile ./auth_service

run_auth_prod:
	docker compose --profile prod-like -f auth_service/docker-compose.yaml up -d

stop_auth_prod:
	docker compose --profile prod-like -f auth_service/docker-compose.yaml down -v

# main launch
create_network:
	docker network create online_cinema

build_main:
	docker build -t watch_together_service -f ./docker/Dockerfile . && \
	docker build -t auth-service -f auth_service/docker/Dockerfile ./auth_service

run_main:
	docker compose -f docker-compose.yaml up -d && \
	docker compose --profile prod-like -f auth_service/docker-compose.yaml up -d

stop_main:
	docker compose -f docker-compose.yaml down -v && \
	docker compose --profile prod-like -f auth_service/docker-compose.yaml down -v
