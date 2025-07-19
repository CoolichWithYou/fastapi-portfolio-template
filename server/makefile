.PHONY: lint test install

SRC=. tests

lint:
	@echo "Running isort..."
	isort $(SRC)

	@echo "Running black..."
	black $(SRC)

	@echo "Running flake8..."
	flake8 $(SRC)

run:
	@echo "Running db"
	cd ../ && \
	sudo docker compose up --build -d db && \
	uvicorn server.main:app --host 0.0.0.0 --port 8000 --env-file .env.example

test:
	cd ../ && \
	sudo docker compose up --build -d db && \
	export $$(grep -v '^#' .env.example | xargs) && \
	cd server && \
	make prod_test

migrate:
	@echo "Running db"
	cd ../ && \
	export $$(grep -v '^#' .env | xargs) && \
	sudo docker compose up --build -d db && \
	alembic -c ./server/alembic.ini upgrade head

install:
	pip install -r requirements.txt

up:
	sudo docker compose up --build

down:
	sudo docker compose down

prod_test:
	@echo "Running tests with pytest..."
	pytest --cache-clear

prod_migrate:
	@echo "Applying migrations in alembic/versions..."
	cd ../ && alembic -c /server/alembic.ini upgrade head
