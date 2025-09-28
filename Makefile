PHONY: upgrade downgrade migrate run logs down lint type hooks commit

SRC=src

type:
	uv run mypy src

upgrade:
	uv run python -m alembic upgrade head

# make downgrade REV=5d892fa238da
downgrade:
	uv run python -m alembic downgrade $(REV)

# make migrate MSG="initial setup"
migrate:
	uv run python -m alembic revision --autogenerate -m "$(MSG)"


run:
	docker compose up --build -d


logs:
	docker compose logs -f backend


down:
	docker compose down


lint:
	@uv run ruff format .
	@echo "code formatted"
	@uv run ruff check --fix .
	@echo "code checked and fixed if needed"


hooks:
	uv run pre-commit install --hook-type pre-commit --hook-type commit-msg --hook-type pre-push
	uv run pre-commit run --all-files


commit:
	uv run cz commit
