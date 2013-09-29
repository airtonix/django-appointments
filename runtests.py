#!/usr/bin/env python
from djeasytests.testsetup import TestSetup, default_settings


default_settings.update(dict(
    ROOT_URLCONF='test_project.urls',
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    },
    INSTALLED_APPS=[
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.flatpages',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django.contrib.sitemaps',
        'django.contrib.admin',
        'django.contrib.admindocs',

        'appointments',
        'test_project',
    ],
    MIDDLEWARE_CLASSES=[
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ],
    PASSWORD_HASHERS=(
        'django.contrib.auth.hashers.MD5PasswordHasher',
    ),
    APPOINTMENT_FIRST_DAY_OF_WEEK=1
))

unittests = TestSetup(appname='test_project',
                      default_settings=default_settings)

if __name__ == '__main__':
    unittests.run('tests')
