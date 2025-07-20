.PHONY: lint test install

SRC=. tests

lint:
	@echo "Running isort..."
	isort $(SRC)

	@echo "Running black..."
	black $(SRC)

	@echo "Running flake8..."
	flake8 $(SRC)

up:
	sudo docker compose up --build

down:
	sudo docker compose down

prod_test:
	@echo "Running tests with pytest..."
	pytest --cache-clear

prod_migrate:
	@echo "Applying migrations in alembic/versions..."
	cd / && alembic -c server/alembic.ini upgrade head
