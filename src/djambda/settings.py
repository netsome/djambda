"""
Django settings for djambda project.
"""

import environs

# Read env variables
# https://github.com/sloria/environs
env = environs.Env()


# Build paths inside the project like this: BASE_DIR / '...'
BASE_DIR = env.path("BASE_DIR", default=str(environs.Path(__file__).parents[1]))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str(
    "SECRET_KEY", default="ia_66li-_2c)n73kvp^)f)3$r@2kg!glphw4c3%yj3-@s1f70m"
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", default=True)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "djambda",
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

ROOT_URLCONF = "djambda.urls"

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
            ],
        },
    },
]

WSGI_APPLICATION = "djambda.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

ENABLE_DATABASES = env.str("DATABASE_URL", default="")
if ENABLE_DATABASES:
    DATABASES = {"default": env.dj_db_url("DATABASE_URL")}


## User model
## https://docs.djangoproject.com/en/3.1/ref/settings/#auth-user-model

AUTH_USER_MODEL = "djambda.User"


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",},
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = env.str("LANGUAGE_CODE", default="en-us")

TIME_ZONE = env.str("TIME_ZONE", default="UTC")

USE_I18N = env.bool("USE_I18N", default=True)

USE_L10N = env.bool("USE_L10N", default=True)

USE_TZ = env.bool("USE_TZ", default=True)


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = env.str("STATIC_URL", default="/static/")

STATIC_ROOT = env.str("STATIC_ROOT", default=None)

if env.bool("ENABLE_S3_STORAGE", default=False):
    # https://github.com/etianen/django-s3-storage
    STATICFILES_STORAGE = "django_s3_storage.storage.ManifestStaticS3Storage"
    AWS_ACCESS_KEY_ID = env.str("AWS_S3_ACCESS_KEY_ID_STATIC")
    AWS_SECRET_ACCESS_KEY = env.str("AWS_S3_SECRET_ACCESS_KEY_STATIC")
    AWS_REGION = env.str("AWS_REGION_STATIC")
    AWS_S3_BUCKET_NAME_STATIC = env.str("AWS_S3_BUCKET_NAME_STATIC")
    AWS_S3_BUCKET_AUTH_STATIC = False
    AWS_S3_PUBLIC_URL_STATIC = env.str("AWS_S3_PUBLIC_URL_STATIC", default="")
    AWS_S3_KEY_PREFIX_STATIC = env.str("AWS_S3_KEY_PREFIX_STATIC", default="")
elif env.bool("ENABLE_MANIFEST_STORAGE", default=False):
    # https://docs.djangoproject.com/en/3.1/ref/contrib/staticfiles/#manifeststaticfilesstorage

    STATICFILES_STORAGE = (
        "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
    )


# HTTP
# https://docs.djangoproject.com/en/3.1/ref/settings/#http

FORCE_SCRIPT_NAME = env.str("FORCE_SCRIPT_NAME", default=None)


# Email backends
# https://docs.djangoproject.com/en/3.1/topics/email/#email-backends

if env.bool("ENABLE_SMTP_EMAIL_BACKEND", default=False):
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = env.str("EMAIL_HOST")
    EMAIL_PORT = env.int("EMAIL_PORT")
    EMAIL_HOST_USER = env.str("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = env.str("EMAIL_HOST_PASSWORD")
    EMAIL_USE_TLS = env.str("EMAIL_USE_TLS")
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

DEFAULT_FROM_EMAIL = env.str("DEFAULT_FROM_EMAIL", default="webmaster@localhost")


# Logging
# https://docs.djangoproject.com/en/3.1/topics/logging/

LOGGING_LEVEL = env.str("LOGGING_LEVEL", default="INFO")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {pathname} {message}",
            "style": "{",
        },
        "simple": {"format": "{levelname} {message}", "style": "{",},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "verbose",},
    },
    "loggers": {
        "django": {"handlers": ["console"], "level": LOGGING_LEVEL, "propagate": True,},
    },
}
