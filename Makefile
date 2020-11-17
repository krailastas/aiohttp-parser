.PHONY: install isort isort-check flake check celery-worker celery-beat revision migrate

install:
	pip install -r requirements.txt

isort:
	isort */*.py

isort-check:
	isort -c */*.py

flake:
	flake8 . --max-line-length=80 --exclude=migrations/versions

celery-worker:
	celery -A celery_app worker -B -l info

celery-beat:
	celery -A celery_app beat -l info

check:
	make isort-check && printf "\n\n\n"
	make flake && printf "\n\n\n"

revision:
	alembic revision --autogenerate

migrate:
	alembic upgrade head

