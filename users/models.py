from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from .managers import CustomUserManager

class CustomUser(AbstractBaseUser):
    username = models.CharField(blank=False, max_length=40, unique=True)
    email = models.EmailField('email address', blank=True)
    is_staff = models.BooleanField("is_staff", default=True)
    is_active = models.BooleanField("is_active", default=True)
    is_superuser = models.BooleanField("is_superuser", default=False)
    signed_up_with_google = models.BooleanField(default=False)
    google_id = models.CharField(max_length=255, default='defult_value')
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()
    
    
    def is_staff_user(self):
        return self.is_staff
    
    def is_active_user(self):
        return self.is_active
    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser
    
    def __str__(self):
        return self.username
    


    

    
    
