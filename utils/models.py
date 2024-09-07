from peewee import SqliteDatabase, Model, TextField, IntegerField

db = SqliteDatabase('database.db')


class Users(Model):
    id = IntegerField(primary_key=True)
    user_id = IntegerField()
    username = TextField()
    fullname = TextField()
    number_car = TextField()
    status = IntegerField(default=0)
    points = IntegerField(default=0)
    points_done = IntegerField(default=0)

    class Meta:
        database = db
