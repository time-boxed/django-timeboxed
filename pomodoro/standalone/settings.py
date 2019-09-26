"""
Django settings for standalone project.

Generated by 'django-admin startproject' using Django 1.10.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os
import environ
import pathlib

env = environ.Env()
try:
    environ.Env.read_env(env("DJANGO_ENV_FILE"))
except FileNotFoundError:
    pass

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["*"])


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "social_django",
    "pomodoro.apps.PomodoroConfig",
    "pomodoro.standalone",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "standalone.urls"
SOCIAL_AUTH_RAISE_EXCEPTIONS = DEBUG

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

WSGI_APPLICATION = "pomodoro.standalone.wsgi.application"
ROOT_URLCONF = "pomodoro.standalone.urls"

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {"default": env.db_url("DATABASE_URL", default="sqlite:///db.sqlite3")}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = env("TIME_ZONE", default="UTC")

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = env.path(
    "STATIC_ROOT", default=(pathlib.Path.home() / ".cache" / "pomodoro")
)

MEDIA_URL = "/media/"
MEDIA_ROOT = env.path(
    "MEDIA_ROOT", default=(pathlib.Path.home() / ".local" / "pomodoro" / "media")
)

# Enable Sentry
if "SENTRY_DSN" in os.environ:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.django import DjangoIntegration
        from sentry_sdk.integrations.celery import CeleryIntegration

        sentry_sdk.init(
            dsn=os.environ["SENTRY_DSN"],
            integrations=[DjangoIntegration(), CeleryIntegration()],
            send_default_pii=True,
        )
    except ImportError:
        pass

# See documentation here
# http://psa.matiasaguirre.net/docs/backends/google.html?highlight=google
SOCIAL_AUTH_RAISE_EXCEPTIONS = DEBUG
AUTHENTICATION_BACKENDS = (
    "social_core.backends.google.GooglePlusAuth",
    "django.contrib.auth.backends.ModelBackend",
)
SOCIAL_AUTH_GOOGLE_PLUS_KEY = os.environ.get("SOCIAL_AUTH_GOOGLE_PLUS_KEY")
SOCIAL_AUTH_GOOGLE_PLUS_SECRET = os.environ.get("SOCIAL_AUTH_GOOGLE_PLUS_SECRET")
LOGIN_URL = "/login"
LOGIN_REDIRECT_URL = "/"

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 50,
}


if "CELERY_BROKER_URL" in os.environ:
    CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://127.0.0.1:6379/0")
    CELERY_TIMEZONE = env('CELERY_TIMEZONE', default=TIME_ZONE)
    CELERY_ACCEPT_CONTENT = ["json"]
    CELERY_RESULT_SERIALIZER = "json"
    CELERY_TASK_SERIALIZER = "json"
else:
    CELERY_TASK_ALWAYS_EAGER = True

TEST_RUNNER = "django_nose.NoseTestSuiteRunner"
