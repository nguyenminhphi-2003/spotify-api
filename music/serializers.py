from rest_framework_mongoengine.serializers import DocumentSerializer, EmbeddedDocumentSerializer
from rest_framework import serializers
from music.models import *
from accounts.serializers import UserSerializer
from django.contrib.auth.models import User


class ArtistSerializer(DocumentSerializer):
    class Meta:
        model = Artist
        fields = '__all__'


class SongSerializer(DocumentSerializer):
    artists = ArtistSerializer(many=True, read_only=True)

    artist_ids = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=True
    )

    class Meta:
        model = Song
        fields = ('id', 'title', 'artists', 'artist_ids', 'genre',
                  'file_location', 'image_location', 'duration','lyrics')

    def create(self, validated_data):
        artist_ids = validated_data.pop('artist_ids', None)
        song = Song(**validated_data)

        if artist_ids:
            for artist_id in artist_ids:
                try:
                    artist = Artist.objects.get(id=artist_id)
                    song.artists.append(artist)
                except Artist.DoesNotExist:
                    raise serializers.ValidationError(
                        f"Artist with ID {artist_id} not found")

        return song.save()

    def update(self, instance, validated_data):
        artist_ids = validated_data.pop('artist_ids', None)

        instance.title = validated_data.get('title', instance.title)
        instance.genre = validated_data.get('genre', instance.genre)
        instance.file_location = validated_data.get(
            'file_location', instance.file_location)
        instance.image_location = validated_data.get(
            'image_location', instance.image_location)
        instance.duration = validated_data.get('duration', instance.duration)
        instance.lyrics = validated_data.get('lyrics', instance.lyrics)

        if artist_ids is not None:
            instance.artists = []
            for artist_id in artist_ids:
                try:
                    artist = Artist.objects.get(id=artist_id)
                    instance.artists.append(artist)
                except Artist.DoesNotExist:
                    raise serializers.ValidationError(
                        f"Artist with ID {artist_id} not found")

        instance.save()
        return instance


class AlbumSerializer(DocumentSerializer):
    artists = ArtistSerializer(many=True, read_only=True)
    songs = SongSerializer(many=True, read_only=True)

    artist_ids = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=True
    )

    song_ids = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=True
    )

    class Meta:
        model = Album
        fields = ('id', 'title', 'artists', 'artist_ids',
                  'songs', 'song_ids', 'release_date')

    def create(self, validated_data):
        artist_ids = validated_data.pop('artist_ids', [])
        song_ids = validated_data.pop('song_ids', [])

        album = Album(**validated_data)

        for artist_id in artist_ids:
            try:
                artist = Artist.objects.get(id=artist_id)
                album.artists.append(artist)
            except Artist.DoesNotExist:
                raise serializers.ValidationError(
                    f"Artist with ID {artist_id} not found")

        for song_id in song_ids:
            try:
                song = Song.objects.get(id=song_id)
                album.songs.append(song)
            except Song.DoesNotExist:
                raise serializers.ValidationError(
                    f"Song with ID {song_id} not found")

        return album.save()

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.release_date = validated_data.get(
            'release_date', instance.release_date)

        if 'artist_ids' in validated_data:
            artist_ids = validated_data.pop('artist_ids')
            instance.artists = []
            for artist_id in artist_ids:
                try:
                    artist = Artist.objects.get(id=artist_id)
                    instance.artists.append(artist)
                except Artist.DoesNotExist:
                    raise serializers.ValidationError(
                        f"Artist with ID {artist_id} not found")

        if 'song_ids' in validated_data:
            song_ids = validated_data.pop('song_ids')
            instance.songs = []
            for song_id in song_ids:
                try:
                    song = Song.objects.get(id=song_id)
                    instance.songs.append(song)
                except Song.DoesNotExist:
                    raise serializers.ValidationError(
                        f"Song with ID {song_id} not found")

        instance.save()
        return instance


class PlaylistSerializer(DocumentSerializer):
    # For read operations
    songs = SongSerializer(many=True, read_only=True)
    
    # For write operations
    song_ids = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=True
    )

    class Meta:
        model = Playlist
        fields = ('id', 'title', 'user', 'songs', 'song_ids', 'created_at')

    def create(self, validated_data):
        song_ids = validated_data.pop('song_ids', [])
        
        playlist = Playlist(**validated_data)
        
        for song_id in song_ids:
            try:
                song = Song.objects.get(id=song_id)
                playlist.songs.append(song)
            except Song.DoesNotExist:
                raise serializers.ValidationError(f"Song with ID {song_id} not found")
        
        return playlist.save()

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        
        if 'song_ids' in validated_data:
            song_ids = validated_data.pop('song_ids')
            instance.songs = []
            
            for song_id in song_ids:
                try:
                    song = Song.objects.get(id=song_id)
                    instance.songs.append(song)
                except Song.DoesNotExist:
                    raise serializers.ValidationError(f"Song with ID {song_id} not found")
        
        instance.save()
        return instance