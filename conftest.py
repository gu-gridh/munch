"""
Test configuration for digital humanities projects using pytest

This module provides configuration and fixtures for testing
applications using pytest and Django's testing framework.
"""

import pytest
from django.conf import settings

def pytest_configure(config):
    """Configure fallback Django settings only when pytest-django has not loaded the project settings."""
    if settings.configured:
        return

    settings.configure(
        DEBUG_PROPAGATE_EXCEPTIONS=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:'
            }
        },
        SITE_ID=1,
        SECRET_KEY='test-secret-key',
        USE_I18N=True,
        USE_L10N=True,
        STATIC_URL='/static/',
        ROOT_URLCONF='munch.urls',
        TEMPLATES=[
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'APP_DIRS': True,
                'OPTIONS': {
                    "debug": True,
                },
            },
        ],
        MIDDLEWARE=[
            'django.middleware.common.CommonMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
        ],
        INSTALLED_APPS=[
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.sites',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            'rest_framework',
            'munch.abstract.apps.AbstractConfig',
            'apps.munch.apps.MunchConfig',
        ],
        PASSWORD_HASHERS=[
            'django.contrib.auth.hashers.MD5PasswordHasher',
        ],
        REST_FRAMEWORK={
            'DEFAULT_AUTHENTICATION_CLASSES': [
                'rest_framework.authentication.SessionAuthentication',
                'rest_framework.authentication.BasicAuthentication',
            ],
            'DEFAULT_PERMISSION_CLASSES': [
                'rest_framework.permissions.IsAuthenticatedOrReadOnly',
            ],
            'PAGE_SIZE': 20
        }
    )

