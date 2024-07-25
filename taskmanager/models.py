from django.db import models
from users.models import CustomUser 

class Room(models.Model):
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, blank=False)
    members = models.ManyToManyField(CustomUser, related_name='rooms')
    color = models.CharField(max_length=255, default="#007bff")
    description = models.TextField(blank=True)
    
    def add_member(self, to_add):
        if not self.members.filter(pk=to_add.pk).exists():
            self.members.add(to_add)
            self.save()
    
    def __str__(self):
        return f'{self.id} {self.name}'
    
class FavoritesRoomsList(models.Model):
    user            = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    favorite_rooms  = models.ManyToManyField(Room, blank=True, related_name="favorite_rooms")
    
    def make_favorite(self, room):
        if room not in self.favorite_rooms.all():
            self.favorite_rooms.add(room)
            
            
    def make_not_favorite(self, room):
        if room in self.favorite_rooms.all():
            self.favorite_rooms.remove(room)
    
    def is_favorite(self, room):
        return room in self.favorite_rooms.all()
    

class Project(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='projects')
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    members = models.ManyToManyField(CustomUser, related_name='members')
    name = models.CharField(max_length=50, blank=False)
    date_created = models.DateField(auto_now_add=True)
    color = models.CharField(max_length=50, blank=True)
    
    def add_member(self, member):
        self.members.add(member)
        self.save()
        
    def remove_member(self, member):
        self.members.remove(member)
        self.save()
    
    def __str__(self):
        return f'{self.id} {self.name}'
    
class Section(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='sections')
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return f'{self.id} {self.name}'
    
    
class Task(models.Model):
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="created_by")
    in_section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='tasks')
    name = models.CharField(max_length=50)
    date_created = models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True)
    
    def __str__(self):
        return f'{self.id} {self.name}'
    
class Comments(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="task")
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="comment_by")
    comment = models.TextField()
    date_created = models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True)
    
    def __str__(self):
        return f'{self.id} comment'
    
