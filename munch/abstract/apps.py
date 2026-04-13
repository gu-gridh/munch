"""
Abstract App Configuration

Django app configuration for abstract models.
"""

from django.apps import AppConfig


class AbstractConfig(AppConfig):
    """App configuration for abstract models"""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'munch.abstract'
