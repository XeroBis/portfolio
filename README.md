# portofolio

## COMMAND USED FREQUENTLY

uv run manage.py makemessages -l fr
uv run manage.py makemessages -l en
uv run manage.py makemessages -a
### docker

build prod :
docker compose -f docker-compose.prod.yml up --build -d

build dev :
docker compose -f docker-compose.yml up --build -d

### uv

uv sync --extra dev

## precommit :
black --check .
black .
isort .
flake8 .
pylint apps/ mysite/
mypy apps/ mysite/
bandit -r apps/ mysite/
pip-audit
safety check

### run all :
uv run pre-commit run --all-files
