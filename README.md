# portofolio


## COMMAND USED FREQUENTLY

scp -r 

### docker 

build prod :
docker compose -f docker-compose.prod.yml up --build -d


build dev :
docker compose -f docker-compose.yml up --build -d


docker compose down
docker compose up

remove images : 
docker rmi -f $(docker images -aq)


### nginx

python manage.py collectstatic

sudo systemctl restart nginx

sudo systemctl stop nginx

sudo systemctl start nginx

sudo nano /etc/nginx/sites-available/myproject
