# portofolio


## COMMAND USED FREQUENTLY

scp -r 

### docker 

build prod :
docker compose -f docker-compose.prod.yml up --build -d


build dev :
docker-compose -f docker-compose.yml up --build -d



docker compose up -d

docker compose up -d --build

docker compose down

remove images : 
docker rmi -f $(docker images -aq)

docker compose run django-docker python manage.py makemigrations

docker compose run django-docker python manage.py migrate

docker compose run django-docker python manage.py import_exercice

docker compose run django-docker python manage.py import_workout

### nginx

python manage.py collectstatic

sudo systemctl restart nginx

sudo systemctl stop nginx

sudo systemctl start nginx

sudo nano /etc/nginx/sites-available/myproject
