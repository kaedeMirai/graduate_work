POETRY = ./.venv/bin/poetry



venv: ##@Env Init venv and install poetry dependencies
	@rm -rf .venv || true && \
	python3.11 -m venv .venv && \
	.venv/bin/pip install poetry && \
	${POETRY} install --no-root

migrate:
	alembic upgrade head

run_prod_like:
	docker-compose --profile prod-like up -d

stop_prod_like:
	docker-compose --profile prod-like  down -v

run_dev:
	docker-compose -f docker-compose.yaml -f docker-compose.dev.yaml up -d

stop_dev:
	docker-compose -f docker-compose.yaml -f docker-compose.dev.yaml down -v

run_with_gunicorn:
	gunicorn main:app --bind 0.0.0.0:8000 -k uvicorn.workers.UvicornWorker --log-level=debug

run_with_uvicorn:
	uvicorn main:app --log-level=debug --host=0.0.0.0 --port=8000

build_image:
	docker build -t auth-service -f ./docker/Dockerfile .

run_tests:
	docker-compose -f docker-compose.yaml -f docker-compose.dev.yaml exec auth_service python3 -m pytest -vv tests

create_super_user:
	docker exec -it auth_container python3 scripts/create_super_user.py

