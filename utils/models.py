from peewee import SqliteDatabase, Model, TextField, IntegerField, DateTimeField

db = SqliteDatabase('database.db')


class Users(Model):
    id = IntegerField(primary_key=True)
    user_id = IntegerField()
    username = TextField()
    fullname = TextField()
    number_car = TextField()
    status = IntegerField(
        default=0)  # 0 - не на смене, 1 - в пути на РЦ, 2 - на загрузке, 3 - развозит, 4 - разгружается на точке
    points = IntegerField(default=0)
    points_done = IntegerField(default=0)
    datetime_cancel = DateTimeField(null=True, default=None)
    notify_msg_id = IntegerField(default=0)

    class Meta:
        database = db


class Races(Model):
    id = IntegerField(primary_key=True)
    user_id = IntegerField()
    fullname = TextField()
    number_car = TextField()
    datetime_start = DateTimeField()
    points = IntegerField()
    points_time = TextField(default='')

    class Meta:
        database = db
