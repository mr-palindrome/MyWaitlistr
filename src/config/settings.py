import os
from pathlib import Path

from decouple import config

ENV_NAME = config('ENV_NAME')

MONGO_DB_URI = config('MONGO_DB_URI')
MONGO_DB_NAME = config('MONGO_DB_NAME')

BASE_DIR = Path(__file__).resolve().parent.parent