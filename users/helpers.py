from .models import CustomUser
import random
import string

def generate_random_username(google_name):
    google_first_name = google_name.split()[0]
    if not CustomUser.objects.filter(username=google_first_name).exists():
        return google_first_name
    
    i = 1
        
    while i:
        # Generate a random username
        username = google_first_name + str(i)
        i = i + 1
        
        # Check if the username is already in use
        if not CustomUser.objects.filter(username=username).exists():
            return username