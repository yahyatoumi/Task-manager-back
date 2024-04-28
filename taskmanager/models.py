from django.db import models
from users.models import CustomUser 

class Room(models.Model):
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, blank=False)
    members = models.ManyToManyField(CustomUser, related_name='rooms')
    color = models.CharField(max_length=255, default="#007bff")
    
    def add_member(self, to_add):
        if not self.members.filter(pk=to_add.pk).exists():
            self.members.add(to_add)
            self.save()
    
    def __str__(self):
        return f'{self.id} {self.name}'

class Project(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='room')
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    members = models.ManyToManyField(CustomUser, related_name='projects')
    name = models.CharField(max_length=50, blank=False)
    date_created = models.DateField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        
            
        # Call the parent class's save method to save the instance
        super().save(*args, **kwargs)
        Section.objects.create(project=self, name='To Do')
        Section.objects.create(project=self, name='In Progress')
        Section.objects.create(project=self, name='Done')
    
    def __str__(self):
        return f'{self.id} {self.name}'
    
class Section(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project')
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return f'{self.id} {self.name}'
    
    
class Task(models.Model):
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="created_by")
    in_section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='section')
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
    
