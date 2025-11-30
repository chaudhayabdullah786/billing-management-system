import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SESSION_SECRET') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 300,
        'pool_pre_ping': True,
    }
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    TAX_RATE = 0.18
    LOW_STOCK_THRESHOLD = 10
