from django.urls import path
from . import views
from django.contrib import admin

urlpatterns = [
    path('', views.prof_accueil, name='prof_accueil'),  # Home page
    path('get_class_stats/<int:class_id>/', views.get_class_stats, name='get_class_stats'),
    path('classes/', views.prof_classes, name='prof_classes'),
    path('classes/archive/<int:class_id>/', views.archive_classe, name='archive_classe'),
    path('classes/archived/', views.archived_classes, name='archived_classes'),
    path('classes/archived/unarchive/<int:class_id>/', views.unarchive_classe, name='unarchive_classe'),
    path('notification/', views.prof_notification, name='prof_notification'),
    path('profile/', views.prof_profile, name='prof_profile'),
    path('create_class/', views.create_class, name="create_class"),
    path('edit_classe/<int:class_id>/', views.edit_classe, name="edit_classe"),
    path('delete_classe/<int:class_id>/', views.delete_classe, name="delete_classe"),
    path('classe/<int:class_id>/', views.classe_detail, name="classe_detail"),
    path('classe/<int:class_id>/add_project', views.add_project, name='add_project'),
    path('classe/<int:projet_id>/detail_projet', views.projet_detail, name='projet_detail'),
    path('classe/<int:class_id>/etudiants/', views.classe_etudiants, name='classe_etudiants'),
    path('projet/<int:projet_id>/edit', views.edit_projet, name='edit_projet'),
    path('projet/<int:projet_id>/delete', views.delete_projet, name='delete_projet'),
    path('classe/<int:projet_id>/detail_projet/add-instruction/', views.add_instruction, name='add_instruction'),


    path('update_instructions/<int:project_id>/<int:groupe_id>/', views.update_instruction_status, name='update_instruction_status'),
    path('projet/<int:projet_id>/announce/add/', views.add_announce, name="add_announce"),
    path('announce/<int:announce_id>/delete/', views.delete_announce, name="delete_announce"),
    path('announce/<int:announce_id>/modify/', views.modify_announce, name="modify_announce"),
    path('projet/<int:projet_id>/ressource/add/', views.add_ressource, name="add_ressource"),
    path('ressource/<int:ressource_id>/delete/', views.delete_ressource, name="delete_ressource"),
    path('instruction/<int:id>/edit/', views.edit_instruction, name='edit_instruction'),    
    path('instruction/<int:id>/delete/', views.delete_instruction, name='delete_instruction'),  

    path('projet/<int:projet_id>/groupe/<int:groupe_id>/', views.groupe_stats_view, name='groupe_stats'),
    path('projet/<int:projet_id>/groupe/<int:groupe_id>/notifier/<int:etudiant_id>/<str:champ>/', views.notifier_champ_manquant, name='notifier_champ_manquant'),


    path('pchatbot', views.chat_view, name='pchatbot'),
    path('etudiant/<int:etudiant_id>/supprimer/', views.supprimer_etudiant, name='supprimer_etudiant'),
    path('mes-projets/', views.project_list, name='mes_projets'),

    path('calendar/', views.calendar_view, name='calender'),
    path('calender/add-or-edit-event/', views.add_or_edit_event, name='add_or_edit_event'),
    path("calender/delete-event/<int:event_id>/", views.delete_event, name="delete_event"),


    path('start-meet/', views.start_meet, name='start_meet'),
    path('meet/launch/', views.launch_meet, name='launch_meet'),

    path('notification/', views.prof_notification, name='prof_notification'),
    path('notification/delete/<int:notification_id>/', views.delete_notification, name='delete_notification'),
    path('notification/read/<int:notification_id>/', views.mark_as_read, name='mark_notification_read'),
    path('notification/mark_all_read/', views.mark_all_as_read, name='mark_all_notifications_read'),

]
