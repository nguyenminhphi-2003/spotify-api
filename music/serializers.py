import boto3
from botocore.exceptions import ClientError
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
    song_file = serializers.FileField(write_only=True, required=False)
    image_file = serializers.FileField(write_only=True, required=False)
    artist_ids = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=True
    )

    class Meta:
        model = Song
        fields = '__all__'
        extra_kwargs = {
            'artists': {'read_only': True},  # artists sẽ được tạo từ artist_ids
            'file_location': {'read_only': True},  # file_location do backend tạo
            'image_location': {'read_only': True},  # image_location do backend tạo
        }

    def validate(self, data):
        # Kiểm tra khi tạo mới: song_file và image_file là bắt buộc
        if not self.instance:  # Khi tạo mới
            if 'song_file' not in data or not data['song_file']:
                raise serializers.ValidationError({"song_file": "This field is required."})
            if 'image_file' not in data or not data['image_file']:
                raise serializers.ValidationError({"image_file": "This field is required."})
        return data

    def validate_artist_ids(self, value):
        # Kiểm tra artist_ids
        for artist_id in value:
            if not isinstance(artist_id, str) or len(artist_id) != 24:
                raise serializers.ValidationError(f"'{artist_id}' không phải là ObjectId hợp lệ.")
            if not Artist.objects(id=artist_id).first():
                raise serializers.ValidationError(f"Artist với id '{artist_id}' không tồn tại.")
        return value

    def create(self, validated_data):
        # Lấy file từ validated_data
        song_file = validated_data.pop('song_file', None)
        image_file = validated_data.pop('image_file', None)
        artist_ids = validated_data.pop('artist_ids', [])

        # Upload file audio lên S3
        if song_file:
            s3_client = boto3.client('s3')
            bucket_name = 'nct2k3spotify'  # Thay bằng tên bucket của bạn
            file_name = f"songs/{song_file.name}"
            try:
                s3_client.upload_fileobj(song_file, bucket_name, file_name)
                file_url = f"https://{bucket_name}.s3.amazonaws.com/{file_name}"
                validated_data['file_location'] = file_url
            except ClientError as e:
                raise serializers.ValidationError(f"Không thể upload file audio lên S3: {str(e)}")

        # Upload file hình ảnh lên S3
        if image_file:
            s3_client = boto3.client('s3')
            bucket_name = 'nct2k3spotify'  # Thay bằng tên bucket của bạn
            file_name = f"images/{image_file.name}"
            try:
                s3_client.upload_fileobj(image_file, bucket_name, file_name)
                image_url = f"https://{bucket_name}.s3.amazonaws.com/{file_name}"
                validated_data['image_location'] = image_url
            except ClientError as e:
                raise serializers.ValidationError(f"Không thể upload file hình ảnh lên S3: {str(e)}")

        # Chuyển artist_ids thành artists (ReferenceField)
        validated_data['artists'] = [Artist.objects(id=artist_id).first() for artist_id in artist_ids]

        # Tạo và lưu đối tượng Song
        song = Song(**validated_data)
        song.save()
        return song

    def update(self, instance, validated_data):
        # Lấy file từ validated_data
        song_file = validated_data.pop('song_file', None)
        image_file = validated_data.pop('image_file', None)
        artist_ids = validated_data.pop('artist_ids', None)

        # Upload file audio lên S3 nếu có
        if song_file:
            s3_client = boto3.client('s3')
            bucket_name = 'nct2k3spotify'  # Thay bằng tên bucket của bạn
            file_name = f"songs/{song_file.name}"
            try:
                s3_client.upload_fileobj(song_file, bucket_name, file_name)
                file_url = f"https://{bucket_name}.s3.amazonaws.com/{file_name}"
                validated_data['file_location'] = file_url
            except ClientError as e:
                raise serializers.ValidationError(f"Không thể upload file audio lên S3: {str(e)}")

        # Upload file hình ảnh lên S3 nếu có
        if image_file:
            s3_client = boto3.client('s3')
            bucket_name = 'nct2k3spotify'  # Thay bằng tên bucket của bạn
            file_name = f"images/{image_file.name}"
            try:
                s3_client.upload_fileobj(image_file, bucket_name, file_name)
                image_url = f"https://{bucket_name}.s3.amazonaws.com/{file_name}"
                validated_data['image_location'] = image_url
            except ClientError as e:
                raise serializers.ValidationError(f"Không thể upload file hình ảnh lên S3: {str(e)}")

        # Cập nhật artists nếu có artist_ids
        if artist_ids:
            validated_data['artists'] = [Artist.objects(id=artist_id).first() for artist_id in artist_ids]

        # Cập nhật các trường khác
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class AlbumSerializer(DocumentSerializer):
    artists = serializers.SerializerMethodField(read_only=True)
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

    def get_artists(self, obj):
        if not obj.artists or len(obj.artists) == 0:
            return None
        artist_list = []
        for artist_ref in obj.artists:
            try:
                if isinstance(artist_ref, str):
                    artist_id = artist_ref
                else:
                    artist_id = artist_ref.id

                artist = Artist.objects.get(id=artist_id)
                artist_list.append(ArtistSerializer(artist).data)
            except Exception as e:
                print(f"Error fetching artist: {e}")
                continue

        return artist_list if artist_list else None

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
                raise serializers.ValidationError(
                    f"Song with ID {song_id} not found")

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
                    raise serializers.ValidationError(
                        f"Song with ID {song_id} not found")

        instance.save()
        return instance

class NotificationsSerializer(DocumentSerializer):
    class Meta:
        model = Notifications
        fields = ['id', 'title', 'user', 'created_at']
        read_only_fields = ['created_at']