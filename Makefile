.PHONY: start stop restart logs migrate init-mongo seed health test

start:
	docker compose up -d --build

stop:
	docker compose down

restart: stop start

logs:
	docker compose logs -f

migrate:
	docker compose run --rm tools bash -c "pip install psycopg2-binary && python scripts/migrate.py"

init-mongo:
	docker compose run --rm tools bash -c "pip install pymongo && python scripts/init_mongo.py"

health:
	docker compose run --rm tools bash -c "pip install psycopg2-binary pymongo redis bullmq && python scripts/verify.py"

test: health
