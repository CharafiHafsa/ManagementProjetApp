from django.urls import path
from . import views
from .views import create_class, edit_classe , delete_classe , add_project

urlpatterns = [
    path('', views.prof_accueil, name='prof_accueil'),  # Home page
    path('get_class_stats/<int:class_id>/', views.get_class_stats, name='get_class_stats'),
    path('classes/', views.prof_classes, name='prof_classes'),
    path('notification/', views.prof_notification, name='prof_notification'),
    path('profile/', views.prof_profile, name='prof_profile'),
    path('settings/', views.prof_settings, name= 'prof_settings'),
    path('calender/', views.prof_calender, name='prof_calender'),
    path('create_class/', create_class, name="create_class"),
    path('edit_classe/<int:class_id>/', edit_classe, name="edit_classe"),
    path('delete_classe/<int:class_id>/', delete_classe, name="delete_classe"),
    path('classe/<int:class_id>/', views.classe_detail, name="classe_detail"),
    path('classe/<int:class_id>/add_project', add_project, name='add_project'),
    path('classe/<int:projet_id>/detail_projet', views.projet_detail, name='projet_detail'),
]
