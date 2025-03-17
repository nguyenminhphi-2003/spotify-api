from rest_framework_mongoengine.serializers import DocumentSerializer, EmbeddedDocumentSerializer
from music.models import *


class ArtistSerializer(EmbeddedDocumentSerializer):
    class Meta:
        model = Artist
        fields = '__all__'


class SongSerializer(EmbeddedDocumentSerializer):
    artists = ArtistSerializer(many=True, required=True)

    class Meta:
        model = Song
        fields = ('id', 'title', 'artists', 'genre',
                  'file_location', 'duration')

    def create(self, validated_data):
        artists_data = validated_data.pop('artists')
        song = Song(**validated_data)

        for artist_data in artists_data:
            try:
                artist = Artist.objects.get(name=artist_data['name'])
            except Artist.DoesNotExist:
                artist = Artist.objects.create(**artist_data)
            song.artists.append(artist)

        return song.save()

    def update(self, instance, validated_data):
        artists = validated_data.pop('artists')
        instance.title = validated_data.get('title', instance.title)
        instance.genre = validated_data.get('genre', instance.genre)
        instance.file_location = validated_data.get(
            'file_location', instance.file_location)
        instance.duration = validated_data.get('duration', instance.duration)
        instance.artists = []

        for artist in artists:
            try:
                artist = Artist.objects.get(id=artist['id'])
            except Artist.DoesNotExist:
                artist = Artist.objects.create(**artist)
            instance.artists.append(artist)

        return instance.save()


class AlbumSerializer(DocumentSerializer):
    artists = ArtistSerializer(many=True)
    songs = SongSerializer(many=True)

    class Meta:
        model = Album
        fields = ('id', 'title', 'artists', 'songs', 'release_date')

    def create(self, validated_data):
        artists = validated_data.pop('artists')
        songs = validated_data.pop('songs')
        album = Album(**validated_data)

        for artist in artists:
            try:
                artist = Artist.objects.get(name=artist['name'])
            except Artist.DoesNotExist:
                artist = Artist.objects.create(**artist)
            album.artists.append(artist)

        for song in songs:
            try:
                song = Song.objects.get(title=song['title'])
            except Song.DoesNotExist:
                song = SongSerializer().create(song)
            album.songs.append(song)

        return album.save()

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.release_date = validated_data.get(
            'release_date', instance.release_date)

        if 'artists' in validated_data:
            artists = validated_data.pop('artists')
            instance.artists = []
            for artist in artists:
                try:
                    artist = Artist.objects.get(name=artist['name'])
                except Artist.DoesNotExist:
                    artist = Artist.objects.create(**artist)
                instance.artists.append(artist)

        if 'songs' in validated_data:
            songs = validated_data.pop('songs')
            instance.songs = []
            for song in songs:
                try:
                    song = Song.objects.get(title=song['title'])
                except Song.DoesNotExist:
                    song = SongSerializer().create(song)
                instance.songs.append(song)

        return instance.save()


# class PlaylistSerializer(DocumentSerializer):
#     songs = SongSerializer(many=True)

#     class Meta:
#         model = Playlist
#         fields = ('id', 'title', 'user_id', 'songs', 'created_at')

#     def create(self, validated_data):
#         songs = validated_data.pop('songs')
#         playlist = Playlist(**validated_data)

#         for song in songs:
#             try:
#                 song = Song.objects.get(title=song['title'])
#             except Song.DoesNotExist:
#                 song = SongSerializer().create(song)
#             playlist.songs.append(song)

#         return playlist.save()

#     def update(self, instance, validated_data):
#         instance.title = validated_data.get('title', instance.title)
#         instance.user_id = validated_data.get('user_id', instance.user_id)
#         instance.songs = []

#         songs = validated_data.pop('songs')
#         for song in songs:
#             try:
#                 song = Song.objects.get(title=song['title'])
#             except Song.DoesNotExist:
#                 song = SongSerializer().create(song)
#             instance.songs.append(song)

#         instance.save()
#         return instance
