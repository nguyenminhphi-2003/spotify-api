import datetime
import string

from mongoengine import Document, StringField, IntField, ListField, LazyReferenceField, ReferenceField, DateTimeField, FloatField



class Artist(Document):
    name = StringField(max_length=100, required=True)
    bio = StringField(max_length=1000, required=True)
    artist_photo = StringField(max_length=1000, required=True)
    debut_year = IntField(required=True)


class Song(Document):
    title = StringField(max_length=100, required=True)
    artists = ListField(ReferenceField(Artist), required=False)
    genre = StringField(max_length=100, required=True)
    file_location = StringField()
    image_location = StringField()
    duration = FloatField(required=True)
    lyrics = StringField(max_length=100000, required=True)


class Album(Document):
    title = StringField(max_length=100, required=True)
    artists = ListField(ReferenceField(Artist), required=True)
    songs = ListField(ReferenceField(Song), required=True)
    Album_photo = StringField(max_length=1000)
    Album_type = IntField(required=True)
    release_date = DateTimeField(required=True)


class Playlist(Document):
    title = StringField(max_length=100, required=True)
    user = StringField()
    songs = ListField(ReferenceField(Song), required=True)
    created_at = DateTimeField(default=datetime.datetime.now())

class Notifications(Document):
    title = StringField(max_length=1000, required=True)
    user = StringField()
    created_at = DateTimeField(default=datetime.datetime.now())
    meta = {
        'collection': 'notifications',
        'indexes': [
            'user',
            'created_at',
        ]
    }


