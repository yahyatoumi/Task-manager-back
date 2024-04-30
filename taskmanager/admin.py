from django.contrib import admin
from .models import Room, Project, Section, Task, Comments, FavoritesRoomsList

admin.site.register(Room)
admin.site.register(Project)
admin.site.register(Section)
admin.site.register(Task)
admin.site.register(Comments)
admin.site.register(FavoritesRoomsList)

# Register your models here.
