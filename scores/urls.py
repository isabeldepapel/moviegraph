from django.urls import path

from . import views

app_name = 'scores'

urlpatterns = [
    path('', views.index, name='root'),
    path('index', views.index, name='index'),
    path('validate', views.validate, name='validate'),
    path('actors', views.actors, name='actors'),
    path('search', views.search, name='search'),
    # path('search_json', views.search_json, name='search_json')
]
