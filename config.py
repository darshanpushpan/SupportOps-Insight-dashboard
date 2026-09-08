"""Configuration settings for SupportOps Insight."""

import os


class Config:
    """Base configuration."""

    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    REPORTS_FOLDER = os.path.join(BASE_DIR, 'reports')
    LOGS_FOLDER = os.path.join(BASE_DIR, 'logs')

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'log', 'txt', 'json'}

    SEVERITY_WEIGHTS = {
        'DEBUG': 1,
        'INFO': 2,
        'WARNING': 3,
        'ERROR': 4,
        'CRITICAL': 5,
    }

    CRITICAL_KEYWORDS = [
        'critical',
        'fatal',
        'emergency',
        'database connection failed',
        'out of memory',
        'authentication failed',
        'timeout',
        'exception',
        'crash',
    ]

    CRITICAL_SERVICES = [
        'payment',
        'auth',
        'database',
        'api',
        'gateway',
        'order',
        'checkout',
        'user',
        'security',
    ]

    DEBUG = False


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')


config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
