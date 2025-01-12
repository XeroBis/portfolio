# portofolio


git pull

python manage.py colletstatic

pkill gunicorn

sudo systemctl restart nginx

gunicorn --bind 0.0.0.0:8000 mysiste.wsgi --daemon