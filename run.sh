#!/bin/bash

basedir=$PWD
password=$(openssl rand -hex 20)

echo Name of the application ?
read appname
echo Path of the application ?
read path

if [ "$path" = "" ]
then
    path="."
fi

echo creation of $appname starting in $path

cd $path
mkdir dev
vue create -nf -p $basedir/vue-preset.json frontend
mkdir backend


echo ".env" >> .gitignore
cp $basedir/docker-compose ./dev/docker-compose.yml
sed -i "s/@\$0/$appname/g" ./dev/docker-compose.yml
cp $basedir/env ./dev/.env
sed -i "s/@\$0/$appname/g" ./dev/.env
sed -i "s/@\$1/$password/g" ./dev/.env

cp $basedir/backend-dockerfile ./backend/Dockerfile
cp $basedir/requirements ./backend/requirements.txt

cp $basedir/frontend-dockerfile ./frontend/Dockerfile

docker-compose -f dev/docker-compose.yml run "${appname}_backend" django-admin startproject back .

sed -i "s/ALLOWED_HOSTS = []/ALLOWED_HOSTS = ['*']/g" ./backend/back/settings.py

old_db="DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}"
new_db="DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ['POSTGRES_USER'],
        'USER': os.environ['POSTGRES_USER'],
        'PASSWORD': os.environ['POSTGRES_PASSWORD'],
        'HOST': os.environ['POSTGRES_HOST'],
        'PORT': os.environ['POSTGRES_PORT']
    }
}
"
sed -i -E "s/$old_db/$new_db/g" ./backend/back/settings.py

old_import="from pathlib import Path"
new_import="from pathlib import Path
import os"
sed -i "s/$old_import/$new_import/g" ./backend/back/settings.py
