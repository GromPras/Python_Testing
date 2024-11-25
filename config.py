import os
from pathlib import Path


base_dir = Path(__file__).parent.resolve()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev_key"
    FLASK_ENV = "development"
    DEBUG = True
