# Docker
.PHONY: up
up: create-dev-env
	@docker compose up --build -d

.PHONY: down
down:
	@docker compose down -v

.PHONY: create-dev-env
create-dev-env:
	@test -e .env || cp .env.example .env

# CI/CD
.PHONY: ci-%
ci-%: create-dev-env
	@docker compose run --rm dev sh -c 'make $*'

# Dev
chainlit:
	@poetry run chainlit run src/chat_docs/main.py --port 8080

.PHONY: test
test: type-py lint-py

.PHONY: lint-py
lint-py:
	@# run both ruff format and lint. https://github.com/astral-sh/ruff/issues/8232
	@poetry run ruff format .
	@poetry run ruff check .

.PHONY: type-py
type-py:
	@poetry run mypy .
