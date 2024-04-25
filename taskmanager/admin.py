from django.contrib import admin
from .models import Room, Project, Section, Task, Comments

admin.site.register(Room)
admin.site.register(Project)
admin.site.register(Section)
admin.site.register(Task)
admin.site.register(Comments)

# Register your models here.
