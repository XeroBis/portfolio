# portofolio


## COMMAND
### docker 

sudo docker compose run django-web python manage.py makemigrations

sudo docker compose run django-web python manage.py migrate

sudo docker compose run django-web python manage.py import_exercice

sudo docker compose run django-web python manage.py import_workout

### nginx

sudo systemctl restart nginx

sudo systemctl stop nginx

sudo systemctl start nginx

sudo nano /etc/nginx/sites-available/myproject


### gunicorn

pkill gunicorn

gunicorn --bind 0.0.0.0:8000 mysite.wsgi --daemon

gunicorn --bind unix:/home/ubuntu/portfolio.sock mysite.wsgi --daemon