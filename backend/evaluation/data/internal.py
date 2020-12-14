from pymongo import MongoClient
from pymongo.database import Database, Collection

from config.local_config import get_local_config

client = None
database = None


def connect() -> Database:
    global client, database
    password = get_local_config().pymongo_password
    default_db = "oop_zk_2"
    client = MongoClient(
        f"mongodb+srv://JulianSobott:{password}@cluster0.upkff.mongodb.net/{default_db}?retryWrites=true&w"
        f"=majority")
    database = client.get_database(default_db)
    return database


def _db() -> Database:
    if not database:
        connect()
    return database


def exams() -> Collection:
    return _db().exams


def submissions() -> Collection:
    return _db().submissions
