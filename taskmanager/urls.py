from django.urls import path
from .views import get_rooms, create_room

taskmanagerurlpatterns = [
    path('getRooms', get_rooms),
    path('createRoom', create_room),
]
