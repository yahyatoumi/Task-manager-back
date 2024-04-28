"""
URL configuration for sideproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, re_path, include
from .views import signup, login, google_auth, auth

usersurlpatterns = [
    path('signup', signup),
    path('login', login),
    path('google/auth', google_auth),
    path('auth', auth),
    re_path(r'^auth/', include('drf_social_oauth2.urls', namespace='drf'))
]
