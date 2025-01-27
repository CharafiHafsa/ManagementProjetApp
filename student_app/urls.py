from django.urls import path
from . import views

urlpatterns = [
    path('ws/chat', views.chat, name='chat'),
    path('ws/todo', views.todo_ws, name='todo_ws'),
    path('accueil/todo/', views.todo_home, name='todo_home'),
    path('accueil/calendrier/', views.calender_home, name='calender_home'),
    path('accueil/classes/', views.classes, name='classes'),
]
