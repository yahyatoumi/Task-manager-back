from django.urls import path
from .views import get_rooms, create_room, set_room_to_favorite, set_room_to_not_favorite, room

taskmanagerurlpatterns = [
    path('getRooms', get_rooms),
    path('createRoom', create_room),
    path('makeRoomFavorite', set_room_to_favorite),
    path('makeRoomNotFavorite', set_room_to_not_favorite),
    path('room/<int:id>/', room, name='workspace-detail'),
]
