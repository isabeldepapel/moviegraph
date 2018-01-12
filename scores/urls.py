from django.urls import path

from . import views

app_name = 'scores'

urlpatterns = [
    path('', views.index, name='index'),
    path('index', views.index, name='index'),
    path('validate_name', views.validate_name, name='validate_name'),
    path('submit', views.submit, name='submit'),
]
