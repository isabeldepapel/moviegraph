from django.urls import path

from . import views

app_name = 'scores'

urlpatterns = [
    path('', views.index, name='index'),
    path('index', views.index, name='index'),
    # path('validate', views.validate, name='validate'),
    # path('submit', views.submit, name='submit'),
    path('actors', views.actors, name='actors'),
    path('search', views.search, name='search'),
]
