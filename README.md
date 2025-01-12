# portofolio


## COMMAND

git pull

python manage.py collectstatic

### nginx

sudo systemctl restart nginx

sudo systemctl stop nginx

sudo systemctl start nginx

sudo nano /etc/nginx/sites-available/myproject


### gunicorn

pkill gunicorn

gunicorn --bind 0.0.0.0:8000 mysite.wsgi --daemon

gunicorn --bind unix:/home/ubuntu/portfolio.sock mysite.wsgi --daemon