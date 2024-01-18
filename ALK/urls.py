from django.urls import path
from . import views

urlpatterns = [
    path('result', views.index, name='result'),
    path('', views.upload_file_view, name='alk'),    
]