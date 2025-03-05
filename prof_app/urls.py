from django.urls import path
from . import views
from django.contrib import admin

urlpatterns = [
    path('', views.prof_accueil, name='prof_accueil'),  # Home page
    path('get_class_stats/<int:class_id>/', views.get_class_stats, name='get_class_stats'),
    path('classes/', views.prof_classes, name='prof_classes'),
    path('notification/', views.prof_notification, name='prof_notification'),
    path('profile/', views.prof_profile, name='prof_profile'),
    path('settings/', views.prof_settings, name= 'prof_settings'),
    path('calender/', views.prof_calender, name='prof_calender'),
    path('create_class/', views.create_class, name="create_class"),
    path('edit_classe/<int:class_id>/', views.edit_classe, name="edit_classe"),
    path('delete_classe/<int:class_id>/', views.delete_classe, name="delete_classe"),
    path('classe/<int:class_id>/', views.classe_detail, name="classe_detail"),
    path('classe/<int:class_id>/add_project', views.add_project, name='add_project'),
    path('classe/<int:projet_id>/detail_projet', views.projet_detail, name='projet_detail'),
    path('projet/<int:projet_id>/edit', views.edit_projet, name='edit_projet'),
    path('projet/<int:projet_id>/delete', views.delete_projet, name='delete_projet'),
    path('classe/<int:projet_id>/detail_projet/add-instruction/', views.add_instruction, name='add_instruction'),


    path('update_instructions/<int:project_id>/<int:groupe_id>/', views.update_instruction_status, name='update_instruction_status'),
    path('projet/<int:projet_id>/announce/add/', views.add_announce, name="add_announce"),
    path('announce/<int:announce_id>/delete/', views.delete_announce, name="delete_announce"),
    path('announce/<int:announce_id>/modify/', views.modify_announce, name="modify_announce"),
    path('projet/<int:projet_id>/ressource/add/', views.add_ressource, name="add_ressource"),
    path('ressource/<int:ressource_id>/delete/', views.delete_ressource, name="delete_ressource"),

    path('chat', views.chat_view, name='chat'),
    
    


]
