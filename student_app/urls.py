from django.urls import path
from . import views

urlpatterns = [
    path('espaceDeTravail/<int:groupe_id>/', views.ws_reception, name='ws_reception'),
    path('ws/chat/', views.chat, name='chat'),
    path('ws/memberes/', views.memberes, name='membres'),
    path('ws/documents/', views.documents, name='documents'),
    path('suppDoc/', views.suppDoc, name='suppDoc'),
    path('quitter-groupe/', views.Quitter_Modifier, name='Quitter_Modifier'),
    path('ws/chatbot/', views.chatbot_view, name='chatbot'),
    path('get_conversation/<int:sujet_id>/', views.get_conversation, name='get_conversation'),
    path('ws/todo/', views.todo_ws, name='todo_ws'),
    path('accueil/todo/', views.todo_home, name='todo_home'),
    path('accueil/calendrier/', views.calender_home, name='calender_home'),
    path('accueil/dashBoard/', views.dashBoard_home, name='dashBoard_home'),
    path('ws/dashBoard/', views.dashBoard_ws, name='dashBoard_ws'),
    path('get_taches_stats_1/', views.get_taches_stats_1, name='get_taches_stats_1'), # bars _home
    path('get_taches_stats_2/', views.get_taches_stats_2, name='get_taches_stats_2'), # courbe principale _home
    path("update_time_counter/", views.update_time_counter, name="update_time_counter"),
    path("ws/detailles/", views.detailles, name="detailles"),
    path("detailles/", views.detailles_sg, name="detailles_sg"),
    path("get_temps_utilisation_chart/", views.get_temps_utilisation_chart, name="get_temps_utilisation_chart"),
    path('classes/', views.classes, name='classes'),
    path('notifications/', views.notifications, name='notifications'),
    path('groupes/', views.groupes, name='groupes'),
    path('groupes/archive', views.groupes_archive, name='groupes_archive'),
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
