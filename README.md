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
