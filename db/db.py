from peewee import SqliteDatabase

from conf.conf import db_path

db = SqliteDatabase(db_path)
