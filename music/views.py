from rest_framework_mongoengine import viewsets
from music.models import *
from music.serializers import *


class ArtistViewSet(viewsets.ModelViewSet):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer


class SongViewSet(viewsets.ModelViewSet):
    queryset = Song.objects.all()
    serializer_class = SongSerializer

class AlbumViewSet(viewsets.ModelViewSet):
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer
    
# class PlaylistViewSet(viewsets.ModelViewSet):
#     queryset = Playlist.objects.all()
#     serializer_class = PlaylistSerializer