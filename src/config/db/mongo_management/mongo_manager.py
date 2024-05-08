from pymongo import MongoClient
from pymongo.server_api import ServerApi
import certifi

from src.config.settings import MONGO_DB_URI, MONGO_DB_NAME

mongo_client = MongoClient(MONGO_DB_URI, tlsCAFile=certifi.where())
mongo_db = mongo_client[MONGO_DB_NAME]


waitlist_collection = mongo_db["waitlist"]
