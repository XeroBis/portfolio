# portofolio


git pull

python manage.py collectstatic

pkill gunicorn

sudo systemctl restart nginx

gunicorn --bind 0.0.0.0:8000 mysite.wsgi --daemon