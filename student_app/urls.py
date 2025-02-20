from django.urls import path
from . import views

urlpatterns = [
    path('espaceDeTravail/<int:groupe_id>/', views.ws_reception, name='ws_reception'),
    path('ws/chat/', views.chat, name='chat'),
    path('ws/memberes/', views.memberes, name='membres'),
    path('ws/documents/', views.documents, name='documents'),
    path('ws/todo/', views.todo_ws, name='todo_ws'),
    path('accueil/todo/', views.todo_home, name='todo_home'),
    path('accueil/calendrier/', views.calender_home, name='calender_home'),
    path('classes/', views.classes, name='classes'),
    path('notifications/', views.notifications, name='notifications'),
    path('groupes/', views.groupes, name='groupes'),
    path('projets/<str:classe_id>/', views.projets, name='projets'),
    path('profil/', views.profil, name='profil'),
    path('api/', views.get_events, name='get_events'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_user, name='logout'),
    path('ws/documents/ouvrir/', views.ouvrir_doc, name='ouvrir_doc'),
    path('forget_password/', views.forget_password, name='forget_password'),
    path('update_password/', views.update_password, name='update_password'),
]
