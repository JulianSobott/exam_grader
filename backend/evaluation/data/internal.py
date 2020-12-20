from pymongo import MongoClient
from pymongo.database import Database, Collection

from config.local_config import get_local_config

client = None
database = None


def connect() -> Database:
    global client, database
    mongo_config = get_local_config().mongodb
    if mongo_config.run_local:
        client = MongoClient('mongodb://localhost:27017/exam_grader')
    else:
        client = MongoClient(mongo_config.url)
    database = client.get_database()
    return database


def _db() -> Database:
    if not database:
        connect()
    return database


def exams() -> Collection:
    return _db().exams


def submissions() -> Collection:
    return _db().submissions
