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
    return """FROM python:3

RUN useradd -m -d /app -s /bin/bash backend
USER backend
ENV PYTHONUNBUFFERED 1
ADD requirements.txt /app/requirements.txt
WORKDIR /app/

RUN pip install --no-cache-dir --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt


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
"""

def get_default_layout():
    return """<template>
  <div>
    <nav-bar />

    <slot />
    <v-footer app dark>
      <footer-bar />
    </v-footer>
  </div>
</template>

<script>
import NavBar from "@/components/NavBar";
import FooterBar from "@/components/FooterBar";

export default {
  components: {
    NavBar,
    FooterBar,
  },
};
</script>
"""

def get_footerbar():
    return """<template>
    <v-container>
        Footer
    </v-container>
</template>

<script>
export default {
    name: 'FooterBar'
}
</script>
"""

def get_navbar():
    return """<template>
  <v-app-bar color="rgba(0, 0, 0, 0.8)">
    <router-link class="link" to="/" id="title">Title</router-link>
    <v-spacer></v-spacer>
  </v-app-bar>
</template>

<script>
export default {
  name: "NavBar"
};
</script>

<style scoped>
#title {
  color: #969fff !important;
}
</style>
"""

def get_app():
    return """<template>
  <v-app>
    <v-main>
      <v-component :is='layout'>
        <router-view/>
      </v-component>
    </v-main>
  </v-app>
</template>

<script>
const default_layout = 'default';

export default {
  name: 'App',
  computed: {
    layout() {
      return (this.$route.meta.layout || default_layout) + '-layout';
    }
  }
};
</script>

<style>
.link {
  color: #000000 !important;
  text-decoration: none;
}
</style>
"""

def get_main():
    return """import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import vuetify from './plugins/vuetify'

import Default from './layouts/Default.vue'

Vue.component('default-layout', Default);

Vue.config.productionTip = false

new Vue({
  router,
  store,
  vuetify,
  render: h => h(App)
}).$mount('#app')
"""

def get_api():
    return """import axios from 'axios'

const api = axios.create({
    baseURL: 'http://127.0.0.1:8000/API/',
    timeout: 1000,
    withCredentials: false
});

function changeToken(token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`
}

async function getTest() {
    const response = await api.get('test/')
    return response
}

async function postTest(body) {
    const response = api.post('test/', { body })
    return response
}
export {
    changeToken,
    getTest,
    postTest
}
"""

def get_test_model():
    return """from django.db import models

class Test(models.Model):
    body = models.TextField()

    def __str__(self):
        return f'{self.body}'
"""

def get_test_serializer():
    return """from rest_framework import serializers
from api.models import test_model

class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = test_model.Test
        fields = '__all__'
"""

def get_test_view():
    return """from rest_framework import generics

from api.models import test_model
from api.serializers import test_serializer

class TestViewSet(generics.ListCreateAPIView):
    queryset = test_model.Test.objects.all()
    serializer_class = test_serializer.TestSerializer
"""

def get_suburl():
    return """from django.urls import path

from api.views import test_view

urlpatterns = [
    path('test/', test_view.TestViewSet.as_view()),
]
"""

def get_url():
    return """from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('API/', include('api.urls'))
]
"""

def get_test_world():
    return """<template>
  <v-container>
    <v-row>
      <v-col>
        <v-btn fab @click.stop="getMsg">
          <v-icon>mdi-download</v-icon>
        </v-btn>
        <v-text-field
          v-model="message"
          append-outer-icon="mdi-send"
          @click:append-outer="saveMsg"
        >
        </v-text-field>
      </v-col>
      <v-col>
        <v-list v-for="msg in messages" :key="msg.id">
          {{ msg.body }}
        </v-list>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { getTest, postTest } from "@/API";

export default {
  name: "HelloWorld",
  data() {
    return {
      message: null,
      messages: [],
    };
  },
  methods: {
    getMsg() {
      getTest().then((response) => {
        this.messages = response.data;
      });
    },
    saveMsg() {
      postTest(this.message).then(() => this.getMsg());
    },
  },
  created() {
    this.getMsg();
  },
};
</script>
"""