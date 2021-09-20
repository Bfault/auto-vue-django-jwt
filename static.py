def get_docker_compose(appname):
    return f"""version: '3.8'

services:
    {appname}_backend:
        container_name: {appname}_backend
        build:
            context: ../backend
        command: python manage.py runserver 0.0.0.0:8000
        environment:
            POSTGRES_HOST: ${{POSTGRES_HOST}}
            POSTGRES_DB: ${{POSTGRES_DB}}
            POSTGRES_PORT: ${{POSTGRES_PORT}}
            POSTGRES_USER: ${{POSTGRES_USER}}
            POSTGRES_PASSWORD: ${{POSTGRES_PASSWORD}}
            DJANGO_SECRET_KEY: ${{DJANGO_SECRET_KEY}}
        volumes:
            - ../backend:/app
        ports:
            - 8000:8000
        networks:
            {appname}_network:
        depends_on:
            - {appname}_db
        restart: unless-stopped
    
    {appname}_db:
        container_name: {appname}_db
        image: postgres
        volumes:
            - ../postgres-data:/var/lib/postgresql/data
        environment:
            POSTGRES_DB: ${{POSTGRES_DB}}
            POSTGRES_USER: ${{POSTGRES_USER}}
            POSTGRES_PASSWORD: ${{POSTGRES_PASSWORD}}
        ports:
            - 5432:5432
        networks:
            {appname}_network:
        restart: unless-stopped
    
    {appname}_frontend:
        container_name: {appname}_frontend
        build:
            context: ../frontend
        command: yarn serve
        volumes:
            - ../frontend:/app
        ports:
            - 8080:8080
        networks:
            {appname}_network:
        depends_on:
            - {appname}_backend
        restart: unless-stopped

networks:
    {appname}_network:
"""

def get_env(appname, token):
    return f"""POSTGRES_HOST={appname}_db
POSTGRES_DB=postgres
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD={token}
"""

def get_front_dockerfile():
    return """FROM node:15.3.0-alpine

ARG NODE_ENV=test
ENV node_env=$(NODE_ENV)

COPY . /app/
WORKDIR /app/

RUN yarn install

EXPOSE 8080
"""

def get_back_dockerfile():
    return """FROM python:3.9.0

ENV PYTHONUNBUFFERED 1
ADD requirements.txt /app/requirements.txt
WORKDIR /app/

RUN pip install -r requirements.txt
RUN adduser --disabled-password --gecos '' backend_user

USER backend_user

COPY . /app/

EXPOSE 80
"""

def get_requirements():
    return """Django==3.1.3
django-rest-framework==0.1.0
psycopg2-binary==2.8.6
django-cors-headers==3.7.0
djangorestframework-simplejwt==4.8.0
"""

def get_init_settings():
    return """from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']
CORS_ORIGIN_ALLOW_ALL = True

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'corsheaders.middleware.CorsMiddleware'
]

ROOT_URLCONF = 'back.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'back.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ['POSTGRES_USER'],
        'USER': os.environ['POSTGRES_USER'],
        'PASSWORD': os.environ['POSTGRES_PASSWORD'],
        'HOST': os.environ['POSTGRES_HOST'],
        'PORT': os.environ['POSTGRES_PORT']
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = False

USE_L10N = True

USE_TZ = True


STATIC_URL = '/static/'

REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'api.exceptions.core_exception_handler',
    'NON_FIELD_ERRORS_KEY': 'error',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'api.authentication.JWTAuthentication',
    ),
}
"""