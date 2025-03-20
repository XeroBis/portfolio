# portofolio


## COMMAND
### docker 

sudo docker compose up --build

sudo docker compose down

sudo docker compose run django-web python manage.py makemigrations

sudo docker compose run django-web python manage.py migrate

sudo docker compose run django-web python manage.py import_exercice

sudo docker compose run django-web python manage.py import_workout

### nginx

sudo systemctl restart nginx

sudo systemctl stop nginx

sudo systemctl start nginx

sudo nano /etc/nginx/sites-available/myproject
