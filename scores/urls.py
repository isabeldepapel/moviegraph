from django.urls import path

from . import views

app_name = 'scores'

urlpatterns = [
    path('', views.home, name='home'),
    path('home', views.home, name='home'),
    path('index', views.index, name='index'),
    # path('validate', views.validate, name='validate'),
    # path('submit', views.submit, name='submit'),
    path('actors', views.actors, name='actors'),
    path('search', views.search, name='search'),
]
