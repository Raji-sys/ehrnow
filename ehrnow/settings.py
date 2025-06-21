from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, '.env'))


SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
# DEBUG = os.environ.get('DJANGO_DEBUG', '') != 'True'
DEBUG = True

CSRF_TRUSTED_ORIGINS = ['https://*.railway.app']
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
    'accounting',
    'easyaudit',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'ehr.middleware.SessionTimeoutMiddleware',
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

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }
# DATABASES = {
#     'default': dj_database_url.config(
#         default='postgresql://raji:8080mali@localhost:5432/emr',
#         conn_max_age=600
#     )
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ["PGDATABASE"],
        'USER': os.environ["PGUSER"],
        'PASSWORD': os.environ["PGPASSWORD"],
        'HOST': os.environ["PGHOST"],
        'PORT': os.environ["PGPORT"],
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

TIME_ZONE = 'Africa/Lagos'

USE_I18N = False

USE_L10N=True

USE_THOUSAND_SEPARATOR=True

USE_TZ = True

DATE_INPUT_FORMATS = ['%d-%m-%Y'] 
DATETIME_INPUT_FORMAT=['%d-%m-%Y']

LOGIN_REDIRECT_URL = '/'
LOGIN_URL="/login/"
LOGOUT_REDIRECT_URL = '/'

# import os
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# -----------------------------------------------------------------------------
# RAILWAY / PaaS CONFIGURATION
# Uncomment this entire block when you’re deploying on Railway (or similar PaaS)
# -----------------------------------------------------------------------------

STATIC_URL = 'static/'

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
# STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]


STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# -----------------------------------------------------------------------------
# LOCAL UBUNTU + NGINX CONFIGURATION (active)
# -----------------------------------------------------------------------------
# URL prefix for static files
# STATIC_URL = '/static/'

# where `collectstatic` will deposit everything
# STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# if you keep “source” assets here for collectstatic to pick up
# STATICFILES_DIRS = [
    # os.path.join(BASE_DIR, 'static'),
# ]


# -----------------------------------------------------------------------------
# MEDIA (uploads) – same for both
# -----------------------------------------------------------------------------
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


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

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

SESSION_COOKIE_AGE = 60 * 3600  # 1 hour in seconds
# Additional security settings
SESSION_SAVE_EVERY_REQUEST = True  # Refresh session on each request
SESSION_COOKIE_SECURE = False  # HTTPS only (set to False for development)
SESSION_COOKIE_HTTPONLY = True  # Prevent XSS attacks
SESSION_COOKIE_SAMESITE = 'Strict'  # CSRF protection
