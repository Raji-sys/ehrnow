from pathlib import Path
import os
# import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent



# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-jy__!sq&0g^l(!21u%+ab8_iuq8j%nv-!g-ft2k1!@-k%pleln'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'ehr.apps.EhrConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'tailwind',
    'theme',
    'django_filters',
    'django_fastdev',
    'import_export',
    'fontawesomefree',
    'django_quill',
    'pharm',
    'chartjs',
    'inventory',
    'results',    
    'page',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # 'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ehrnow.urls'

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

TAILWIND_APP_NAME='theme'
INTERNAL_IPS=['127.0.0.1']
NPM_BIN_PATH = "/usr/bin/npm"

WSGI_APPLICATION = 'ehrnow.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# DATABASES = {
#     'default': dj_database_url.config(
#         default='postgresql://postgres:postgres@localhost:5432/audaxemr',
#         conn_max_age=600
#     )
# }
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': 'emr',
#         'USER': 'raji',
#         'PASSWORD': '8080mali',
#         'HOST': 'localhost',
#         'PORT': '',
#     }
# }
# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Lagos'

USE_I18N = False

USE_L10N=True

USE_THOUSAND_SEPARATOR=True

USE_TZ = True

DATE_INPUT_FORMATS = ['%d-%m-%Y'] 
DATETIME_INPUT_FORMAT=['%d-%m-%Y']

LOGIN_REDIRECT_URL = '/'
LOGIN_URL="/login/"
LOGOUT_REDIRECT_URL = '/logout/'

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# This production code might break development mode, so we check whether we're in DEBUG mode
# if not DEBUG:
#     STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
#     STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, 'node_modules', 'cornerstone-tools', 'dist'),
# ]

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

QUILL_CONFIGS = {
    'default': {
        'theme': 'snow',
        'modules': {
            'syntax': True,
            'toolbar': [
                [
                    {'font': []},
                    {'header': []},
                    {'align': []},
                    'bold', 'italic', 'underline', 'strike', 'blockquote',
                    {'color': []},
                    {'background': []},
                    {'script': 'sub'},
                    {'script': 'super'}, 
                ],
                ['code-block', 'link'],
                ['clean'],
            ]
        }
    }
}
