from django.http import JsonResponse ,HttpResponse,FileResponse,Http404,HttpResponseBadRequest
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode 
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.sites.shortcuts import get_current_site 
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.hashers import make_password
from django.core.files.storage import default_storage
from django.contrib.auth import login,logout
from django.core.mail import send_mail
import google.generativeai as genai
from base_de_donnee.models import *
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from datetime import date
import markdown
from google.api_core.exceptions import ServiceUnavailable, DeadlineExceeded
import uuid
import os
import random
from django.urls import path
import time
from django.db.models import Q
from django.db import transaction
import locale
import calendar
import datetime
from django.utils.text import slugify
import logging
from urllib.parse import urlencode
from urllib.parse import unquote

def logout_user(request):
    update_time_counter(request)
    request.session.flush()
    logout(request)
    
    return redirect('login')

def detailles(request):
    if request.session.get('user_type') != 'etudiant': return redirect('login')

    groupe_id = request.session.get('groupe_id', None)
    groupe = get_object_or_404(Groupe, id=groupe_id)
    projet = groupe.projet
    instructions = projet.instructions.all()
    ressources = projet.ressources.all()
    Annonces = projet.annonces.all()



    if request.method == 'POST':
        instruction_id = request.POST.get('id_instruction') or request.POST.get('instruction_id')
        instruction = get_object_or_404(Instruction, id=instruction_id)

        uploaded_file = None
        for file_key in request.FILES:
            if file_key.startswith("file_"):
                uploaded_file = request.FILES[file_key]
                break

        # Récupérer ou créer le statut
        status, created = InstructionStatus.objects.get_or_create(
            instruction=instruction,
            groupe=groupe
        )

        if instruction.livrable_requis:
            # Si livrable, on gère l'upload
            if uploaded_file:
                status.fichier_livrable = uploaded_file
                status.est_termine = True
        else:
            # Sinon, on gère juste la checkbox
            # Si la case existe dans POST, elle est cochée
            status.est_termine = 'is_checked' in request.POST

        status.save()
        return redirect("detailles")

    # Préparer les données pour le template
    instructions_data = []
    for instruction in instructions:
        try:
            status = InstructionStatus.objects.get(instruction=instruction, groupe=groupe)
        except InstructionStatus.DoesNotExist:
            status = None

        instructions_data.append({
            'instruction': instruction,
            'est_termine': status.est_termine if status else False,
            'fichier_livrable': status.fichier_livrable if status else None,
        })

    grp_avec_projet = request.session.get('grp_avec_projet', None)
    return render(request, 'workSpace/detailles.html', {
        'instructions_data': instructions_data,
        'ressources': ressources,
        'description': projet.description,
        'Annonces':Annonces,
        'grp_avec_projet':grp_avec_projet
    })

def detailles_sg(request):
    if request.session.get('user_type') != 'etudiant': return redirect('login')
    if request.method == 'POST' and 'detailles' in request.POST:
        projet = get_object_or_404(Project, id=request.POST.get('projcet_id'))
        instructions = projet.instructions.all()
        ressources = projet.ressources.all()
        Annonces = projet.annonces.all()

        return render(request, 'singleSections/detailles_sg.html', {
            'instructions': instructions,
            'ressources': ressources,
            'description': projet.description,
            'Annonces':Annonces,
        })

def dashBoard_ws(request):
    if request.session.get('user_type') != 'etudiant': return redirect('login')
    grp_avec_projet = request.session.get('grp_avec_projet', None)
    groupe_id = request.session.get('groupe_id', None)
    if request.session.get('archive') == False:
        groupe = get_object_or_404(Groupe, id=groupe_id)
        taches_groupe = Taches.objects.filter(groupe=groupe)
    else: 
        groupe = get_object_or_404(GroupeArchive, id=groupe_id)
        taches_groupe = Taches.objects.filter(groupeArchive=groupe)



    # Statistiques des tâches
    nb_taches_terminees = taches_groupe.filter(status="Terminé").count()
    nb_taches_en_cours = taches_groupe.filter(deadline__gte=timezone.now().date(), status="En cours").count()
    nb_taches_retard = taches_groupe.filter(deadline__lt=timezone.now().date(), status="En cours").count()
    nb_tache_total = taches_groupe.count()
    if request.session.get('archive') == False:
        nb_membres = Etudiant.objects.filter(groupes=groupe).count()
    else:
        nb_membres = Etudiant.objects.filter(groupesArchive=groupe).count()


    # Si le groupe a un projet
    if groupe.projet:
        projet = groupe.projet
        date_actuelle = date.today()

        # Durée totale du projet
        duree_totale = projet.date_fin - projet.date_debut

        # Calcul du pourcentage de temps écoulé
        if date_actuelle > projet.date_fin:
            pourcentage = 100
        else:
            temps_ecoule = date_actuelle - projet.date_debut
            pourcentage = (temps_ecoule.days / duree_totale.days) * 100

        # Jours restants avant la fin du projet
        jours_restants = (projet.date_fin - date_actuelle).days

        # Pourcentage des tâches effectuées (en évitant la division par zéro)
        if nb_tache_total > 0:
            pourcentage_effectue = (nb_taches_terminees / nb_tache_total) * 100
        else:
            pourcentage_effectue = 0

        return render(request, 'workSpace/dashBoard.html', {
            'projet': projet,
            'pourcentage': int(pourcentage),
            'pourcentage_taches': int(pourcentage_effectue),
            'jours_restants': jours_restants,
            'groupe': groupe,
            'nb_tache_termine': nb_taches_terminees,
            'nb_tache_en_cours': nb_taches_en_cours,
            'nb_taches_retard': nb_taches_retard,
            'nb_tache_total': nb_tache_total,
            'nb_tache_non_realisé': nb_taches_en_cours + nb_taches_retard,
            'grp_avec_projet': grp_avec_projet,
            'nb_membres': nb_membres,
        })

    # Si le groupe n'a pas de projet
    return render(request, 'workSpace/dashBoard.html', {
        'nb_tache_termine': nb_taches_terminees,
        'nb_tache_en_cours': nb_taches_en_cours,
        'nb_taches_retard': nb_taches_retard,
        'nb_tache_total': nb_tache_total,
        'nb_tache_non_realisé': nb_taches_en_cours + nb_taches_retard,
        'grp_avec_projet': grp_avec_projet,
        'nb_membres': nb_membres,
        'pourcentage_taches': 0  
    })

def dashBoard_home(request):
    if request.session.get('user_type') != 'etudiant': return redirect('login')
    id_etudiant = request.session.get('user_id')
    etudiant = Etudiant.objects.filter(id=id_etudiant).first()

    # Récupérer tous les enregistrements de TempsUtilisation pour cet étudiant
    temps_utilisation = TempsUtilisation.objects.filter(etudiant=etudiant)

    # Calculer la somme des durées et le nombre d'enregistrements
    total_temps = timedelta(seconds=0)
    for temps in temps_utilisation:
        total_temps += temps.temps_passe

    # Calculer la moyenne en divisant par le nombre d'enregistrements
    if len(temps_utilisation) > 0:
        moyenne_temps = total_temps / len(temps_utilisation)
    else:
        moyenne_temps = timedelta(seconds=0)

    # Convertir la moyenne en heures et minutes (format 'hh:mm')
    heures = moyenne_temps.seconds // 3600
    minutes = (moyenne_temps.seconds % 3600) // 60
    moyenne_temps_formattee = f"{heures}h {minutes}min"

    update_time_counter(request)
    # Passer la moyenne au template
    return render(request, 'home/dashBoard.html', {
        'moyenne_temps': moyenne_temps_formattee,
        'etudiant': etudiant,
    })

def get_taches_stats_1(request):
    if request.session.get('user_type') != 'etudiant': return redirect('login')
    id_etudiant = request.session.get('user_id')
    etudiant = Etudiant.objects.filter(id=id_etudiant).first()
    
    if not etudiant:
        return JsonResponse({"error": "Utilisateur non authentifié"}, status=403)

    groupes = Groupe.objects.all()
    data = []

    for groupe in groupes:
        taches = groupe.taches.all()  # Récupère toutes les tâches du groupe
        total_taches = taches.count()
        taches_terminees = taches.filter(status="Terminé").count()
        taches_en_cours = taches.filter(status="En cours").count()
        taches_depassees = taches.filter(deadline__lt=date.today(), status="En cours").count()
        mes_taches = taches.filter(etudiant=etudiant).count()

        data.append({
            "nom_groupe": groupe.nom_groupe,
            "total_taches": total_taches,
            "taches_terminees": taches_terminees,
            "taches_en_cours": taches_en_cours,
            "taches_depassees": taches_depassees,
            "mes_taches": mes_taches,
        })

    return JsonResponse({"stats": data})

def get_taches_stats_2(request):
    if request.session.get('user_type') != 'etudiant': return redirect('login')
    id_etudiant = request.session.get('user_id')
    etudiant = Etudiant.objects.get(id=id_etudiant)

    # Récupérer le'historique
    historique = HistoriqueTachesEtu.objects.filter(etudiant=etudiant).order_by('date')

    # Convertir en format utilisable pour le graphique
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')  # Assurez-vous que 'fr_FR.UTF-8' est disponible sur votre système
    categories = [h.date.strftime('%a') for h in historique]  # Renvoie 'Lun', 'Mar', 'Mer', ...
    taches_en_retard = [h.taches_en_retard for h in historique]
    taches_terminees = [h.taches_terminees for h in historique]
    taches_en_cours = [h.taches_en_cours for h in historique]

    data = {
        "categories": categories,
        "series": [
            {"name": "En retard", "data": taches_en_retard},
            {"name": "Términées", "data": taches_terminees},
            {"name": "En cours", "data": taches_en_cours},
        ]
    }

    return JsonResponse(data)

def get_temps_utilisation_chart(request):
    if request.session.get('user_type') != 'etudiant': return redirect('login')
    # Récupérer les 7 derniers jours de temps d'utilisation
    historique = TempsUtilisation.objects.order_by('-date')[:7]

    # Extraire les labels (jours) et les valeurs (temps passé en heures et minutes)
    categories = []
    data = []

    for entry in reversed(historique):  # Reverse pour avoir l'ordre correct (du plus ancien au plus récent)
        jour_nom = calendar.day_name[entry.date.weekday()]  # Nom du jour en anglais
        jour_fr = {
            "Monday": "Lundi", "Tuesday": "Mardi", "Wednesday": "Mercredi",
            "Thursday": "Jeudi", "Friday": "Vendredi", "Saturday": "Samedi", "Sunday": "Dimanche"
        }.get(jour_nom, jour_nom)  # Traduction en français

        # Convertir `temps_passe` en heures et minutes
        total_minutes = entry.temps_passe.total_seconds() // 60
        heures = int(total_minutes // 60)
        minutes = int(total_minutes % 60)
        temps_formate = f"{heures}h {minutes}min" if heures > 0 else f"{minutes}min"

        categories.append(jour_fr)  # Ajouter le nom du jour
        data.append(total_minutes)  # Ajouter la durée en minutes (pour l'échelle)

    # Retourner les données sous format JSON
    return JsonResponse({"categories": categories, "data": data})

def update_time_counter(request):
    if request.session.get('user_type') != 'etudiant': return redirect('login')
    id_etudiant = request.session.get('user_id')
    etudiant = Etudiant.objects.filter(id=id_etudiant).first()
    
    # Récupérer l'heure d'entrée depuis la session, utiliser now() si non défini
    heure_entree_str = request.session.get('heure_entree', timezone.now().isoformat())

    try:
        # Convertir en datetime aware
        heure_entree = datetime.datetime.fromisoformat(heure_entree_str)  # Récupération correcte avec fuseau horaire
    except ValueError:
        return  # En cas d'erreur, ne rien faire

    # Calcul de la durée passée
    temps_passe = timezone.now() - heure_entree
    print('heure_entree',  heure_entree)
    print('temps passé',  temps_passe)
    print('timezone.now()',  timezone.now())

    # Récupérer ou créer l'historique du jour
    historique, created = TempsUtilisation.objects.get_or_create(
        etudiant=etudiant,
        date=timezone.now().date(),
        defaults={
            'temps_passe': timedelta(seconds=0),
            'date_start_counter': heure_entree
        }
    )

    # Mettre à jour le temps passé
    # if historique.date_start_counter == heure_entree:
    #     historique.temps_passe = temps_passe
    # else: historique.temps_passe += temps_passe
    
    historique.temps_passe += temps_passe
    historique.save()

    # update date_entrée pour le calcule suivant de la duré
    heure_entree = timezone.now().isoformat()
    request.session['heure_entree'] = heure_entree

def enregistrer_historique_taches_du_jour(request):
    if request.session.get('user_type') != 'etudiant': return redirect('login')
    id_etudiant = request.session.get('user_id')
    etudiant = Etudiant.objects.filter(id=id_etudiant).first()
    aujourd_hui = timezone.now().date()

    # Vérifier si l'historique d'aujourd'hui existe déjà
    historique, created = HistoriqueTachesEtu.objects.get_or_create(etudiant=etudiant, date=aujourd_hui)

    # Compter les tâches pour l'étudiant
    taches = Taches.objects.filter(etudiant=etudiant)
    historique.taches_en_cours = taches.filter(status="En cours").count()
    historique.taches_terminees = taches.filter(status="Terminé").count()
    historique.taches_en_retard = taches.filter(status="En cours", deadline__lt=aujourd_hui).count()

    # Sauvegarder les changements
    historique.save()

    # Supprimer les anciens enregistrements après 7 jours
    # date_limite = aujourd_hui - timedelta(days=7)
    # HistoriqueTachesEtu.objects.filter(etudiant=etudiant, date__lt=date_limite).delete()

def gerer_notification(request, id_etudiant, etudiant):
    # Prmière page affiché: checker les deadlines et envoyer des rappels
    jours_avant_deadline = 1
    nombre_de_lettres = 10
    today = date.today()
    date_limite_max = today - timedelta(days=15)

    taches_proches = Taches.objects.filter(
        etudiant_id=id_etudiant,
        status="En cours",
        deadline__gte=today,  # Exclut les tâches déjà dépassées.
        deadline__lte=today + timedelta(days=jours_avant_deadline),  # Sélectionne uniquement les tâches dont la deadline est dans les prochains jours.
        groupe__isnull=False
    )
    taches_depassees = Taches.objects.filter(
        etudiant_id=id_etudiant,
        status="En cours",
        deadline__lt=today,
        deadline__gte=date_limite_max,  # Exclut celles dépassées de +15 jours
        groupe__isnull=False
    )

    # Convertir les tâches en une liste de dictionnaires sérialisables
    taches_proches_data = [
        {
            'id': tache.id,
            'description_tache': tache.description_tache[:nombre_de_lettres]+'...',
            'groupe': tache.groupe.nom_groupe,
        }
        for tache in taches_proches
    ]
    taches_depassees_data = [
        {
            'id': tache.id,
            'description_tache': tache.description_tache[:nombre_de_lettres]+'...',
            'groupe': tache.groupe.nom_groupe,
        }
        for tache in taches_depassees
    ]

    # Sauvegarder dans la session
    request.session['taches_proches'] = taches_proches_data
    request.session['taches_depassees'] = taches_depassees_data
    # mettre un signe s'il y a une nouvelle notification
    nouvelle_notifications = False
    if taches_proches_data != [] or taches_depassees_data != [] : 
        nouvelle_notifications = True

    
    # supprimer les notifications de prof qui ont depassé une durée précise
    duree_jours = 5
    limite = timezone.now() - timedelta(days=duree_jours)
    anciennes_notifications = PENotification.objects.filter(created_at__lt=limite)
    count, _ = anciennes_notifications.delete()

    return nouvelle_notifications

def todo_home(request):
    if request.session.get('user_type') != 'etudiant': return redirect('login')
    id_etudiant = request.session.get('user_id')
    etudiant = Etudiant.objects.filter(id=id_etudiant).first()
    # Prmière page affiché: checker les deadlines et envoyer des rappels
    
    today = date.today()
    nouvelle_notifications = gerer_notification(request, id_etudiant, etudiant)
  


    # ---- ^^^ NOTIFICATIONS------------------------------------------------------------------------------------------------------------------------------------------------------------------

    if request.method == 'POST' :
        if 'delete' in request.POST:
            id_tache = request.POST.get('id_tache')
            tache = get_object_or_404(Taches, id=id_tache)
            tache.delete()
        if 'modifier' in request.POST: 
            id_tache = request.POST.get("id-tache")
            tache = get_object_or_404(Taches, id=id_tache)
            # Mise à jour 
            tache.description_tache = request.POST.get('description')
            tache.deadline = request.POST.get('Date')
            tache.save() 
        elif 'status_check' in request.POST: 
            id_tache = request.POST.get("id_tache")
            tache = get_object_or_404(Taches, id=id_tache) 
            tache.status = request.POST.get("status_check")
            tache.save()
        enregistrer_historique_taches_du_jour(request)

    # ----DASHBOARD-------------------------------------------------------------------------------------------

    aujourd_hui = timezone.now().date()
    # Récupérer le dernier enregistrement
    dernier_historique = HistoriqueTachesEtu.objects.filter(etudiant=etudiant).order_by('-date').first()

    if dernier_historique: # recuperer data du dernier jour enregistrer
        derniere_date = dernier_historique.date
        taches_en_cours = dernier_historique.taches_en_cours
        taches_terminees = dernier_historique.taches_terminees
        taches_en_retard = dernier_historique.taches_en_retard
    else: # cas où BDD est vide
        derniere_date = None
        taches_en_cours = 0
        taches_terminees = 0
        taches_en_retard = 0

    # Ajouter les jours manquants
    if not derniere_date or derniere_date < aujourd_hui:
        nouvelle_date = derniere_date + timedelta(days=1) if derniere_date else aujourd_hui
        while nouvelle_date <= aujourd_hui:
            HistoriqueTachesEtu.objects.create(
                etudiant=etudiant,
                date=nouvelle_date,
                taches_en_cours=taches_en_cours,
                taches_terminees=taches_terminees,
                taches_en_retard=taches_en_retard
            )
            nouvelle_date += timedelta(days=1)

        # Supprimer les entrées de plus de 7 jours
        date_limite = aujourd_hui - timedelta(days=7)
        HistoriqueTachesEtu.objects.filter(etudiant=etudiant, date__lt=date_limite).delete()

    # ---TEMPS PASSÉ SUR PLATEFORME-------------------------------------------------------------------------------------------

    # Récupérer l'heure actuelleet la Stocker dans la session
    heure_entree = timezone.now().isoformat()
    request.session['heure_entree'] = heure_entree
    try:
        # Convertir en datetime aware
        heure_entree = datetime.datetime.fromisoformat(heure_entree) # Récupération correcte avec fuseau horaire
    except ValueError:
        return


    aujourd_hui = timezone.now().date()
    dernier_jour = aujourd_hui - timedelta(days=7)

    # Récupérer les entrées existantes des 7 derniers jours
    historique = TempsUtilisation.objects.filter(etudiant=etudiant, date__gte=dernier_jour)

    # Convertir en dictionnaire {date: temps_passe}
    dates_enregistrees = {entry.date: entry.temps_passe for entry in historique}

    # Compléter les jours manquants avec 0
    nouvelles_entrees = []
    for i in range(7):
        jour = aujourd_hui - timedelta(days=i)
        if jour not in dates_enregistrees:
            nouvelles_entrees.append(TempsUtilisation(etudiant=etudiant, date=jour, temps_passe=timedelta(seconds=0)))
    
    # Récupérer l'enregistrement du jour
    last_day = TempsUtilisation.objects.filter(
        etudiant=etudiant, 
        date=timezone.now().date()
    ).first()
    # last_day.date_start_counter = heure_entree
    # last_day.save() 
    print(last_day)

    # Ajouter les nouvelles entrées en une seule requête
    TempsUtilisation.objects.bulk_create(nouvelles_entrees)

    # Supprimer les enregistrements au-delà des 7 derniers jours
    TempsUtilisation.objects.filter(etudiant=etudiant, date__lt=dernier_jour).delete()

    
    enregistrer_historique_taches_du_jour(request)
    taches = Taches.objects.filter(etudiant=etudiant)
    return render(request, 'home/todo.html', {'taches': taches, 'nouvelle_notifications':nouvelle_notifications, 'today':today.isoformat()})

def todo_ws(request):
    if request.session.get('user_type') != 'etudiant': return redirect('login')

    id_etudiant = request.session.get('user_id')
    print('ccc',id_etudiant)
    etudiant = get_object_or_404(Etudiant, id=id_etudiant ) 
    today = datetime.date.today()
    nouvelle_notifications = gerer_notification(request, id_etudiant, etudiant)
    # Récupérer l'ID du groupe depuis la session
    groupe_id = request.session.get('groupe_id', None)
    if request.session.get('archive') == False: 
        groupe = get_object_or_404(Groupe, id=groupe_id)
    else:
        groupe = get_object_or_404(GroupeArchive, id=groupe_id)
    
    if request.method == 'POST' :
        # SUPPRIMER
        if 'delete' in request.POST:
            id_tache = request.POST.get('id_tache')
            tache = get_object_or_404(Taches, id=id_tache)
            tache.delete()
            return redirect('todo_ws')

        # AJOUTER OU MODIFIER
        elif 'modifier-ajouter' in request.POST: 
            toModifie = request.POST.get('toModifie')
            etudiant = None
            if 'etu' in request.POST: 
                id_etudiant = request.POST.get("etu")
                etudiant = get_object_or_404(Etudiant, id=id_etudiant ) 
            description = request.POST.get('description')
            date = request.POST.get('Date')

            # AJOUTER
            if toModifie == "":
                tache = Taches.objects.create(etudiant=etudiant, deadline=date, description_tache=description, status='En cours', groupe=groupe)
            # MODIFIER
            else:
                id_tache = request.POST.get("id-tache") 
                tache = get_object_or_404(Taches, id=id_tache)
                if etudiant != None: 
                    tache.etudiant=etudiant
                tache.description_tache = description
                tache.deadline = date
                tache.save() 

        # MODIFIER LE STATUT DE LA TACHE
        elif 'status_check' in request.POST: 
            id_tache = request.POST.get("id_tache") 
            tache = get_object_or_404(Taches, id=id_tache) 
            tache.status = request.POST.get("status_check")
            tache.save()

        # SAUVGARDER L'HISTORIQUE
        enregistrer_historique_taches_du_jour(request)

    if request.session.get('archive') == False:   
        taches = Taches.objects.filter(groupe=groupe)
        etudiants=Etudiant.objects.filter(groupes=groupe)
    else:
        taches = Taches.objects.filter(groupeArchive=groupe)
        etudiants=Etudiant.objects.filter(groupesArchive=groupe)

    archive = request.session.get('archive')

    grp_avec_projet = request.session.get('grp_avec_projet', None)
    return render(request, 'workSpace/todo.html', {'taches':taches,'etudiants':etudiants, 'groupe_id':groupe_id, 'today':today.isoformat(),' nouvelle_notifications' :nouvelle_notifications, 'archive':archive, 'grp_avec_projet':grp_avec_projet})

def ws_reception(request, groupe_id):
    if request.session.get('user_type') != 'etudiant': return redirect('login')

    est_archive = request.GET.get('archive', 'false').lower() == 'true'
    request.session['archive'] = est_archive

    request.session['groupe_id'] = groupe_id

    if est_archive:
        groupe = get_object_or_404(GroupeArchive, id=groupe_id)
    else:
        groupe = get_object_or_404(Groupe, id=groupe_id)

    if groupe.projet:
        request.session['grp_avec_projet'] = True
    else:
        request.session['grp_avec_projet'] = False

    grp_avec_projet = request.session.get('grp_avec_projet', None)
    return render(request, 'workSpace/ws_reception.html', {'groupe_id':groupe_id, 'grp_avec_projet':grp_avec_projet})

def chat(request):
    if request.session.get('user_type') != 'etudiant': return redirect('login')
    # Récupérer l'ID du groupe depuis la session
    print("chat: ", request.session.get('groupe_id', None))
    groupe_id = request.session.get('groupe_id', None)
    archive = request.session.get('archive')

    # groupe_id = request.GET.get('groupe_id', 1)  
    if groupe_id:
        if request.session.get('archive') == False:
            groupe = Groupe.objects.get(id=groupe_id)
            messages = Message.objects.filter(groupe=groupe).order_by("date_envoi")
        else:
            groupe = GroupeArchive.objects.get(id=groupe_id)
            messages = Message.objects.filter(groupeArchive=groupe).order_by("date_envoi")


        grp_avec_projet = request.session.get('grp_avec_projet', None)
        return render(request, 'workSpace/chat.html', {'messages': messages, 'groupe': groupe, 'grp_avec_projet':grp_avec_projet,'archive':archive})
    else:
        return HttpResponse('Aucun groupe choisi.')
    
def creer_reunion(request, groupe_id):
    if request.session.get('user_type') != 'etudiant': return redirect('login')
    groupe = get_object_or_404(Groupe, id=groupe_id)
    
    # Générer un nom de réunion unique
    nom_reunion = f"{groupe.nom_groupe.replace(' ', '')}_{groupe.id}"
    url_reunion = f"https://meet.jit.si/{nom_reunion}"

    # Tu peux ici enregistrer cet URL si tu veux historiser

    return JsonResponse({"url": url_reunion})

def memberes(request):
    if request.session.get('user_type') != 'etudiant': return redirect('login')
    id_etudiant_connecte = request.session.get('user_id')
    etudiant_connecte = Etudiant.objects.filter(id=id_etudiant_connecte).first()
    grp_avec_projet = request.session.get('grp_avec_projet', None)
    # Récupérer l'ID du groupe depuis la session
    groupe_id = request.session.get('groupe_id', None)
    if request.session.get('archive') == False: 
        etudiants = Etudiant.objects.filter(groupes=groupe_id)
    else:
        etudiants = Etudiant.objects.filter(groupesArchive=groupe_id)

    if request.method == "POST":
        # Suppression d’un membre du groupe
        if "delete" in request.POST:
            # récupère l’ID de l’étudiant à supprimer
            etudiant_id = request.POST.get("id_etudiant")
            etudiant = get_object_or_404(Etudiant, id=etudiant_id)
            # retire du groupe (archivé ou pas) 
            if request.session.get('archive') == False: 
                etudiant.groupes.remove(groupe_id) 
            else:
                etudiant.groupesArchive.remove(groupe_id) 

            return render(request, 'workSpace/membres.html', {'etudiants': etudiants,'etudiant_connecte':etudiant_connecte, 'grp_avec_projet':grp_avec_projet})
        
        # Ajout (invitation) d’un membre via email
        if "btn-add" in request.POST: 
                email = request.POST.get("email") 
                  # Vérification du format de l'email   Il doit se terminer par '-etu@etu.univh2c.ma'."
                if not email.endswith('-etu@etu.univh2c.ma'):
                    return render(request, 'workSpace/membres.html', {
                        'etudiants': etudiants,
                        'etudiant_connecte': etudiant_connecte,
                        'error_message': "L'email n'est pas valide.",
                        'grp_avec_projet': grp_avec_projet
                    })
                # L'étudiant existe dans la base 
                try:
                    etudiant = Etudiant.objects.get(email_etudiant=email) 

                    if request.session.get('archive') == False: 
                    # Vérifier si l'étudiant est déjà membre du groupe 
                        if etudiant.groupes.filter(id=groupe_id).exists():
                            # si l"email est de l'etudiant  authentifié
                            if etudiant.id == etudiant_connecte.id:
                                error_message = "Vous êtes déjà membre de ce groupe."
                            # si l"email est d'un autre etudiant qui est membre de groupe
                            else:
                                error_message = "Cet étudiant est déjà membre de ce groupe."
                            return render(request, 'workSpace/membres.html', {
                                'etudiants': etudiants,
                                'etudiant_connecte': etudiant_connecte,
                                'error_message':  error_message,
                                'grp_avec_projet': grp_avec_projet
                            })
                    else:
                                if etudiant.groupesArchive.filter(id=groupe_id).exists():
                                    if etudiant.id == etudiant_connecte.id:
                                            error_message = "Vous êtes déjà membre de ce groupe."
                                    else:
                                            error_message = "Cet étudiant est déjà membre de ce groupe."
                                    return render(request, 'workSpace/membres.html', {
                                        'etudiants': etudiants,
                                        'etudiant_connecte': etudiant_connecte,
                                        'error_message':  error_message,
                                        'grp_avec_projet': grp_avec_projet
                                    })
                    if request.session.get('archive') == False: 
                        groupe = Groupe.objects.get(id=groupe_id) 
                        
                       
                        invitation_existante = Notification.objects.filter(etudiant=etudiant, groupe=groupe).exists()
                        # envoyer invitation s'il n'est pas déja envoyé mais il n'a pas encore accepté
                        if not invitation_existante:
                            Notification.objects.create(etudiant=etudiant, groupe=groupe)
                            success_message = "Invitation envoyée avec succès"
                       
                        else:
                            success_message = "Une invitation a déjà été envoyée déja a ce étudiant "
                    
                    return render(request, 'workSpace/membres.html', {
                        'etudiants': etudiants,
                        'etudiant_connecte': etudiant_connecte,
                        'success_message': success_message,
                        'grp_avec_projet': grp_avec_projet
                    })
                # l'etudiant n'existe pas dans la base de données 
                except Etudiant.DoesNotExist:
                    return render(request, 'workSpace/membres.html', {
                        'etudiants': etudiants,
                        'etudiant_connecte': etudiant_connecte,
                        'error_message': "Cet email n'existe pas dans la base de données",
                        'grp_avec_projet': grp_avec_projet
                    })

    archive = request.session.get('archive')
    return render(request, 'workSpace/membres.html', {'etudiants': etudiants, 'etudiant_connecte':etudiant_connecte,'archive':archive, 'grp_avec_projet':grp_avec_projet})

def ouvrir_doc(request):
    if request.method == "POST":
        file_url = request.POST.get('file_path')

        if not file_url or not file_url.startswith(settings.MEDIA_URL):
            raise Http404("Fichier introuvable")

        # Décode les caractères spéciaux (comme %C3%A9 → é)
        file_url = unquote(file_url)

        # Reconstruit le chemin absolu du fichier
        file_path = os.path.join(settings.MEDIA_ROOT, file_url[len(settings.MEDIA_URL):])

        if not os.path.exists(file_path):
            raise Http404("Fichier introuvable sur le serveur")

        return FileResponse(open(file_path, 'rb'), content_type='application/octet-stream')

    raise Http404("Méthode non autorisée")

def documents(request):
    if request.session.get('user_type') != 'etudiant': return redirect('login')
    archive = request.session.get('archive')

    if request.session.get('archive') == False:
        groupe_instance = Groupe.objects.get(id=request.session.get('groupe_id'))
    else:
        groupe_instance = GroupeArchive.objects.get(id=request.session.get('groupe_id'))

    etu = Etudiant.objects.get(id=request.session.get('user_id'))

    if request.method == "POST":
        file = request.FILES.get("file")

        if not file:
            return JsonResponse({"success": False, "error": "Aucun fichier sélectionné"}, status=400)

        if request.session.get('archive') == False:
            document = Document(title=os.path.splitext(file.name)[0], file=file, groupe=groupe_instance, etudiant=etu)
        else: 
            document = Document(title=os.path.splitext(file.name)[0], file=file, groupeArchive=groupe_instance, etudiant=etu)
            
        document.save()

        return JsonResponse({"success": True, "id": document.id,"title": document.title, "file_url": document.file.url})  

    grp_avec_projet = request.session.get('grp_avec_projet', None)

    if request.session.get('archive') == False:
        return render(request, 'workSpace/documents.html', {'doc': Document.objects.filter(groupe=groupe_instance), 'grp_avec_projet':grp_avec_projet ,'archive':archive})
    else:
        return render(request, 'workSpace/documents.html', {'doc': Document.objects.filter(groupeArchive=groupe_instance), 'grp_avec_projet':grp_avec_projet, 'archive':archive})

def suppDoc(request):
    if request.session.get('user_type') != 'etudiant': return redirect('login')
    if request.method == 'POST' and 'delete' in request.POST:

        document_id = request.POST.get('document_id')
        
        if document_id:
            document = get_object_or_404(Document, id=document_id)
            document.delete()
            return redirect('documents')
        return HttpResponse("Requête invalide", status=400)
        
def Quitter_Modifier(request):

    if request.session.get('user_type') != 'etudiant': return redirect('login')

    

    if request.method == 'POST':
        if 'delete_groupe' in request.POST:
            groupe_id = request.POST.get('id_groupe_quitter')
            print("GroupeId delete : ", groupe_id)
            if groupe_id:
                etudiant = get_object_or_404(Etudiant, id=request.session.get('user_id'))  

                if request.session.get('archive') == False:
                    print("I'm not archived")
                    groupe = get_object_or_404(Groupe, id=groupe_id)
                    etudiant.groupes.remove(groupe)  # Retirer le groupe de la relation many-to-many
                else:
                    print("I am archived")
                    groupe_archive = get_object_or_404(GroupeArchive, id=groupe_id)
                    etudiant.groupesArchive.remove(groupe_archive)

                return redirect(request.META.get('HTTP_REFERER', 'default_url'))


            
        elif 'modifier_groupe' in request.POST:
            groupe_id = request.POST.get('id_groupe')
            groupe_name = request.POST.get('nom_groupe')
            print("GroupeId modifier : ",groupe_id)
           
            if groupe_id:
                groupe = get_object_or_404(Groupe,id=groupe_id)
                groupe.nom_groupe = groupe_name
                groupe.save()
                return redirect(request.META.get('HTTP_REFERER', 'default_url'))
            
    return HttpResponse("Requête invalide", status=400)

def chatbot_view(request):
    genai.configure(api_key="AIzaSyBNRe5yW4uRQNmjg1GcEZEpiXuPysY7xrQ")
    archive = request.session.get('archive')
    try:
        # Récupérer l'étudiant et le groupe depuis la session
        etudiant_id = request.session.get('user_id')
        groupe_id = request.session.get('groupe_id')

        if not etudiant_id or not groupe_id:
            return JsonResponse({'error': 'Identifiants utilisateur ou groupe manquants.'}, status=400)

        etudiant = Etudiant.objects.filter(id=etudiant_id).first()
        if request.session.get('archive') == False:
            groupe = Groupe.objects.filter(id=groupe_id).first()
        else:
            groupe = GroupeArchive.objects.filter(id=groupe_id).first()


        if not etudiant or not groupe:
            return JsonResponse({'error': 'Étudiant ou groupe non trouvé.'}, status=400)

        # Récupérer tous les sujets associés au groupe
        if request.session.get('archive') == False:
            sujets = Sujet.objects.filter(groupe=groupe).order_by('-id')
        else:
            sujets = Sujet.objects.filter(GroupeArchive=groupe).order_by('-id')

        # Gérer la requête POST
        if request.method == 'POST':
           
            action = request.POST.get('action')
            
            if action == 'clear_session':
                # Effacer le sujet de la session pour une nouvelle conversation
                if 'sujet_id' in request.session:
                    del request.session['sujet_id']
                return JsonResponse({'success': True})
            
            elif action == 'set_session_subject':
                # Définir le sujet actuel dans la session
                subject_id = request.POST.get('subject_id')
                if subject_id:
                    request.session['sujet_id'] = subject_id
                return JsonResponse({'success': True})
            
            # Traitement normal des messages
            user_message = request.POST.get('message', '').strip()

            if not user_message:
                return JsonResponse({'error': 'Le message ne peut pas être vide.'}, status=400)

            
            sujet_id = request.session.get('sujet_id')
            sujet = None
            
            if sujet_id:
                sujet = Sujet.objects.filter(id=sujet_id).first()

            # Créer un nouveau sujet si aucun n'existe
            if not sujet:
                sujet = Sujet.objects.create(
                    titre=f"Conversation sur : {user_message[:30]}{'...' if len(user_message) > 30 else ''}",
                    groupe=groupe
                )
                request.session['sujet_id'] = sujet.id

            # Envoyer le message au chatbot
            model = genai.GenerativeModel("gemini-2.0-flash")
            chat = model.start_chat()

            max_retries = 5  # Nombre maximal de tentatives
            delay = 1.0  # Délai initial avant réessai (en secondes)
            multiplier = 2.0  # Facteur multiplicateur du délai

            response = None

            for attempt in range(max_retries):
                try:
                    response = chat.send_message(
                        f"{user_message} (Réponds de manière claire et précise.)",
                        generation_config={
                            "max_output_tokens": 300,
                            "temperature": 0.7,
                            "top_p": 0.9,
                            "top_k": 40
                        }
                    )
                    break  # Sortir de la boucle si la requête réussit

                except (ServiceUnavailable, DeadlineExceeded) as e:
                    if attempt < max_retries - 1:
                        time.sleep(delay)  # Attendre avant de réessayer
                        delay *= multiplier  # Augmenter le délai d'attente
                    else:
                        return JsonResponse({'error': 'Erreur de connexion au service de chatbot.'}, status=503)

            if not response or not response.text:
                return JsonResponse({'error': 'Réponse vide du chatbot.'}, status=500)

            formatted_response = markdown.markdown(response.text)

            # Sauvegarder le message de l'étudiant
            ChatMessage.objects.create(etudiant=etudiant, sujet=sujet, contenu=user_message)

            # Sauvegarder la réponse du chatbot
            ChatMessage.objects.create(etudiant=None, sujet=sujet, contenu=response.text)

            
            return JsonResponse({
                'response': formatted_response,
                'subject_id': sujet.id,
                'subject_title': sujet.titre
            })

        # Afficher la page avec les sujets disponibles
        grp_avec_projet = request.session.get('grp_avec_projet', None)
        return render(request, 'WorkSpace/chatbot.html', {
            'sujets': sujets, 
            'grp_avec_projet': grp_avec_projet,
            'archive':archive
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_conversation(request, sujet_id):
    try:
        sujet = Sujet.objects.filter(id=sujet_id).first()

        if not sujet:
            return JsonResponse({'error': 'Sujet non trouvé.'}, status=404)

        messages = ChatMessage.objects.filter(sujet=sujet).order_by('id')

        conversation_data = [
            {
                'contenu': message.contenu, 
                'etudiant': message.etudiant.nom if message.etudiant else 'Chatbot',
                'id': message.id
            }
            for message in messages
        ]

        return JsonResponse({
            'messages': conversation_data,
            'subject_title': sujet.titre
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# def classes(request): 
#     if request.session.get('user_type') != 'etudiant': return redirect('login')
#     id_etudiant = request.session.get('user_id')
#     etudiant = Etudiant.objects.filter(id=id_etudiant).first()

#      # ✅ Récupérer les classes non archivées pour cet étudiant
#     classes_data = Classe.objects.filter(
#         etudiantsclasse__etudiant=etudiant,
#         etudiantsclasse__is_archived=False
#     )

#     # 🔹 Dossier correct avec faute volontaire si tu l’as bien écrit comme ça
#     default_images_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'defaullt_classe_images')
#     all_images = [f for f in os.listdir(default_images_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]

#     classes_with_images = []
#     for classe in classes_data:
#         random_image = random.choice(all_images) if all_images else None
#         classes_with_images.append({
#             'classe': classe,
#             'image': f'img/defaullt_classe_images/{random_image}' if random_image else None
#         })

#     if request.method == "POST":
#          # 🔹 Cas: rejoindre une classe
#         code_class = request.POST.get('code_classe')
#         if code_class:
#             classe = Classe.objects.filter(code_classe=code_class).first()
#             if classe:
#                 if classe not in etudiant.classes.all():
#                     etudiant.classes.add(classe)
#                     etudiant.save()
#                     return redirect("classes")
#             else:
#                 return render(request, "singleSections/classes.html", {
#                     "classes_with_images": classes_with_images,
#                     "error_message": "Ce code de classe est invalide.",
#                 })

#         # 🔹 Cas: quitter une classe
#         id_quitter = request.POST.get('id_groupe_quitter')
#         if id_quitter:
#             classe_a_quitter = Classe.objects.filter(id=id_quitter).first()
#             if classe_a_quitter and classe_a_quitter in etudiant.classes.all():
#                 etudiant.classes.remove(classe_a_quitter)
#                 etudiant.save()
#                 return redirect("classes")
        
#        # 🔹 Cas: archiver une classe
#         id_archiver = request.POST.get('class_id')
#         if request.POST.get('archiver') and id_archiver:
#             classe_a_archiver = Classe.objects.filter(id=id_archiver).first()
#             if classe_a_archiver:
#                 print(f"[DEBUG] ➤ Classe à archiver : {classe_a_archiver.nom_classe}")

#                 # Étape 1 : archiver la classe
#                 classe_a_archiver.is_archived = True
#                 classe_a_archiver.save()
#                 print("[DEBUG] ✔ Classe archivée.")

#                 # Étape 2 : parcourir tous les projets de cette classe
#                 projets = Project.objects.filter(code_classe=classe_a_archiver)
#                 print(f"[DEBUG] ➤ Projets trouvés : {projets.count()}")

#                 for projet in projets:
#                     print(f"[DEBUG] ➤ Projet : {projet.nom_project}")

#                     # Étape 3 : archiver tous les groupes du projet
#                     groupes = Groupe.objects.filter(projet=projet)
#                     print(f"[DEBUG] ➤ Groupes trouvés pour ce projet : {groupes.count()}")

#                     for groupe in groupes:
#                         print(f"[DEBUG] Archiver groupe : {groupe.nom_groupe}")

#                         # Créer une copie dans GroupeArchive
#                         GroupeArchive.objects.create(
#                             nom_groupe=groupe.nom_groupe,
#                             nbr_membre=groupe.nbr_membre,
#                             projet=projet
#                         )
#                         # Supprimer le groupe original
#                         groupe.delete()

#                 print("[DEBUG] ✔ Tous les groupes archivés.")
#                 return redirect("classes")
#             else:
#                 print("[DEBUG] ❌ Classe introuvable pour l'ID donné.")



#     return render(request, 'singleSections/classes.html', {
#         'classes_with_images': classes_with_images
#     })



def classes(request): 
    if request.session.get('user_type') != 'etudiant':
        return redirect('login')
    
    id_etudiant = request.session.get('user_id')
    etudiant = Etudiant.objects.filter(id=id_etudiant).first()
    
    #  Récupérer les classes non archivées pour cet étudiant
    classes_data = Classe.objects.filter(
    etudiantclasse__etudiant=etudiant,
    etudiantclasse__is_archived=False
)


    #  Charger les images aléatoires
    default_images_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'defaullt_classe_images')
    all_images = [f for f in os.listdir(default_images_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]

    classes_with_images = []
    for classe in classes_data:
        random_image = random.choice(all_images) if all_images else None
        classes_with_images.append({
            'classe': classe,
            'image': f'img/defaullt_classe_images/{random_image}' if random_image else None
        })

    if request.method == "POST":

        # Rejoindre une classe
        code_class = request.POST.get('code_classe')
        if code_class:
            classe = Classe.objects.filter(code_classe=code_class).first()
            if classe:
                relation, created = EtudiantClasse.objects.get_or_create(etudiant=etudiant, classe=classe)
                if created:
                    return redirect("classes")
                elif relation.is_archived:
                    relation.is_archived = False
                    relation.save()
                    return redirect("classes")
            else:
                return render(request, "singleSections/classes.html", {
                    "classes_with_images": classes_with_images,
                    "error_message": "Ce code de classe est invalide.",
                })

        #  Quitter une classe
        id_quitter = request.POST.get('id_groupe_quitter')
        if id_quitter:
            classe_a_quitter = Classe.objects.filter(id=id_quitter).first()
            if classe_a_quitter:
                EtudiantClasse.objects.filter(etudiant=etudiant, classe=classe_a_quitter).delete()
                return redirect("classes")

        #  Archiver une classe
        id_archiver = request.POST.get('class_id')
        if request.POST.get('archiver') and id_archiver:
            classe_a_archiver = Classe.objects.filter(id=id_archiver).first()
            if classe_a_archiver:
                print(f"[DEBUG] ➤ Classe à archiver : {classe_a_archiver.nom_classe}")

                #  Archiver uniquement pour cet étudiant
                relation = EtudiantClasse.objects.filter(etudiant=etudiant, classe=classe_a_archiver).first()
                if relation:
                    relation.is_archived = True
                    relation.save()
                    print("[DEBUG] ✔ Classe archivée pour cet étudiant.")


               
                #  Archiver les groupes de cette classe
                projets = Project.objects.filter(code_classe=classe_a_archiver)
                print(f"[DEBUG] ➤ Projets trouvés : {projets.count()}")

                for projet in projets:
                    groupes = Groupe.objects.filter(projet=projet, membres=etudiant)
                    
                    for groupe in groupes:
                        # traitement d'archivage des groupe
                        print("[DEBUG] groupe",groupe)
                        if not hasattr(groupe, 'archive'):  # True si une archive existe
                                print("[DEBUG] cree a nouveau")
                                with transaction.atomic():  # Garantit que tout est exécuté sans erreur
                                    # 1. Créer une instance dans GroupeArchive
                                    groupe_archive = GroupeArchive.objects.create(
                                        groupe=groupe,
                                        nom_groupe=groupe.nom_groupe,
                                        nbr_membre=groupe.nbr_membre,
                                        projet=groupe.projet
                                    )

                                    # 2. Mettre à jour toutes les relations :

                                    # Taches → groupeArchive
                                    for tache in groupe.taches.all():
                                        tache.groupeArchive = groupe_archive
                                        tache.save()

                                    # Documents → groupeArchive
                                    for document in groupe.documents.all():
                                        document.groupeArchive = groupe_archive
                                        document.save()

                                    # Notifications → groupeArchive
                                    for notification in groupe.notifications.all():
                                        notification.groupeArchive = groupe_archive
                                        notification.save()

                                    # Messages → groupeArchive
                                    for message in groupe.messages.all():
                                        message.groupeArchive = groupe_archive
                                        message.save()

                                    # Sujets → groupeArchive
                                    for sujet in Sujet.objects.filter(groupe=groupe):
                                        sujet.GroupeArchive = groupe_archive
                                        sujet.save()
                        else:
                                print("[DEBUG] deja creé")
                                groupe_archive = groupe.archive

                        # Mettre à jour l'étudiant
                        etudiant.groupes.remove(groupe)  # Retirer du groupe normal
                        etudiant.groupesArchive.add(groupe_archive)  # Ajouter à l'archive

                print("[DEBUG] ✔ Tous les groupes de l'étudiant archivés.")
                return redirect("classes")

    return render(request, 'singleSections/classes.html', {
        'classes_with_images': classes_with_images
    })

def classes_archive(request):
    if request.session.get('user_type') != 'etudiant': return redirect('login')
    id_etudiant = request.session.get('user_id')
    etudiant = Etudiant.objects.filter(id=id_etudiant).first()

    # Récupérer les classes archivées pour cet étudiant (via la relation)
    relations_archivees = EtudiantClasse.objects.filter(etudiant=etudiant, is_archived=True).select_related('classe')
    classes = [rel.classe for rel in relations_archivees]

    if request.method == "POST":
        # desarchiver
        if 'desarchiver' in request.POST:
            classe_id = request.POST.get('class_id')
            relation = EtudiantClasse.objects.filter(etudiant=etudiant, classe_id=classe_id).first()
            if relation:
                relation.is_archived = False
                relation.save()
                print("[DEBUG] ✔ Classe desarchivée pour cet étudiant.")

            
             # Récupérer les projets liés à ces classes archivées
            projets_archives = Project.objects.filter(code_classe__in=classes)

            # 🔹 1. Récupérer les groupes liés aux projets archivés
            groupes = Groupe.objects.filter(projet__in=projets_archives)
            print(f"[DEBUG] ➤ Groupes liés à projets archivés : {groupes.count()}")

            # 🔹 2. Récupérer les groupes archivés liés à ces groupes
            groupes_archives_possibles = GroupeArchive.objects.filter(groupe__in=groupes)
            print(f"[DEBUG] ➤ Groupes archivés possibles : {groupes_archives_possibles.count()}")

            # 🔹 3. Filtrer pour garder uniquement les groupes archivés où l'étudiant est membre
            groupes_archives_etudiant = groupes_archives_possibles.filter(membres=etudiant)
            print(f"[DEBUG] ✔ Groupes archivés où l'étudiant est membre : {groupes_archives_etudiant.count()}")

          
            for groupe_archive in groupes_archives_etudiant:
                groupe = groupe_archive.groupe
                etudiant.groupes.add(groupe)
                etudiant.groupesArchive.remove(groupe_archive)

        # quitter
        elif 'delete_groupe' in request.POST:
           classe_id = request.POST.get('id_groupe_quitter')
           EtudiantClasse.objects.filter(etudiant=etudiant, classe_id=classe_id).delete()

        return redirect('classes_archives')

    

   



    # Exemple d'image par défaut, à adapter selon ta logique
    default_images_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'defaullt_classe_images')
    all_images = [f for f in os.listdir(default_images_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]

    classes_with_images = []
    for classe in classes:
        random_image = random.choice(all_images) if all_images else None
        classes_with_images.append({
            'classe': classe,
            'image': f'img/defaullt_classe_images/{random_image}' if random_image else None
        })

    return render(request, 'singleSections/classesArchive.html', {
        'classes_with_images': classes_with_images
    })

def notifications(request):
    if request.session.get('user_type') != 'etudiant': return redirect('login')
    id_etudiant = request.session.get('user_id')
    etudiant = Etudiant.objects.filter(id=id_etudiant).first()
    notifications = Notification.objects.filter(etudiant=etudiant)
    taches_proches = request.session.get('taches_proches', [])
    taches_depassees = request.session.get('taches_depassees', [])

    pNotifications = []
    for notification in PENotification.objects.all():
        etudiants_notifie = list(notification.etudiants.all())
        if etudiant in etudiants_notifie:
            pNotifications.append(notification)

    if request.method == 'POST' :
        # suprimer une notification
        if 'delete' in request.POST:
            id_notification = request.POST.get('id_notification')
            notification = get_object_or_404(Notification, id=id_notification )
            notification.delete()
            return redirect('notifications')
        elif 'delete_pn' in request.POST:
            id_notification = request.POST.get('id_notification')
            notification = get_object_or_404(PENotification, id=id_notification )
            notification.etudiants.remove(etudiant)
            return redirect('notifications')

        # accepter une invitation
        elif 'accepter' in request.POST:
            id_notification = request.POST.get('id_notification')
            notification  = get_object_or_404(Notification, id=id_notification )
            groupe=notification.groupe
            groupe.membres.add(etudiant)  
            groupe.nbr_membre += 1  
            groupe.save()  
            notification .delete()
            return redirect('notifications')



    return render(request, 'singleSections/notifications.html',  {'taches_proches':taches_proches, 'taches_depassees':taches_depassees , 'notifications':notifications, 'pNotifications':pNotifications})

def groupes(request):
    if request.session.get('user_type') != 'etudiant': return redirect('login')
    id_etudiant = request.session.get('user_id')
    est_archive = request.GET.get('archive', 'false').lower() == 'true'
    request.session['archive'] = est_archive
    etudiant = Etudiant.objects.filter(id=id_etudiant).first()
    
    if request.method == "POST" :
        # archiver le groupe -------------------------------------------------
        if 'archiver' in request.POST:
            group_id = request.POST.get("group_id")
            groupe = get_object_or_404(Groupe, id=group_id)

            if not hasattr(groupe, 'archive'):  # True si une archive existe
                with transaction.atomic():  # Garantit que tout est exécuté sans erreur
                    # 1. Créer une instance dans GroupeArchive
                    groupe_archive = GroupeArchive.objects.create(
                        groupe=groupe,
                        nom_groupe=groupe.nom_groupe,
                        nbr_membre=groupe.nbr_membre,
                        projet=groupe.projet
                    )

                    # 2. Mettre à jour toutes les relations :

                    # Taches → groupeArchive
                    for tache in groupe.taches.all():
                        tache.groupeArchive = groupe_archive
                        tache.save()

                    # Documents → groupeArchive
                    for document in groupe.documents.all():
                        document.groupeArchive = groupe_archive
                        document.save()

                    # Notifications → groupeArchive
                    for notification in groupe.notifications.all():
                        notification.groupeArchive = groupe_archive
                        notification.save()

                    # Messages → groupeArchive
                    for message in groupe.messages.all():
                        message.groupeArchive = groupe_archive
                        message.save()

                    # Sujets → groupeArchive
                    for sujet in Sujet.objects.filter(groupe=groupe):
                        sujet.GroupeArchive = groupe_archive
                        sujet.save()
            else:
                groupe_archive = groupe.archive

            # Mettre à jour l'étudiant
            etudiant.groupes.remove(groupe)  # Retirer du groupe normal
            etudiant.groupesArchive.add(groupe_archive)  # Ajouter à l'archive


        else: # créer un groupe -------------------------------------------------
            
            nom_groupe = request.POST.get("nom_groupe")
            # Récupérer les emails sous forme de liste
            emails = request.POST.get("emails", "").split(",")
            # Créer le groupe
            groupe = Groupe.objects.create(nom_groupe=nom_groupe, nbr_membre=len(emails) + 1)
            groupe.membres.add(etudiant)
            
            
            # Vérifier chaque email et créer les notifications
            for email in emails:
                if email == etudiant.email_etudiant:
                      continue  # On saute cette itération
                etudiant_invite = Etudiant.objects.filter(email_etudiant=email).first()
                if etudiant_invite:
                    Notification.objects.create(etudiant=etudiant_invite, groupe=groupe)
            
                messages.success(request, "Groupe créé avec succès et les invitations sont envoyées !")
    
    groupes = etudiant.groupes.all()
    groupes_data = []
    for groupe in groupes:
        total_taches = groupe.taches.count()
        taches_terminees = groupe.taches.filter(status="Terminé").count()
        progression = (taches_terminees / total_taches * 100) if total_taches > 0 else 0

        groupes_data.append({
            "groupe": groupe,
            "progression": int(progression) 
        })
#    tous les emails  
    tous_emails = Etudiant.objects.values_list('email_etudiant', flat=True)
    
    return render(request, 'singleSections/groupes.html', {"groupes_data": groupes_data,  "emails": list(tous_emails), })

def groupes_archive(request):

    if request.session.get('user_type') != 'etudiant': return redirect('login')
    id_etudiant = request.session.get('user_id')
    etudiant = Etudiant.objects.filter(id=id_etudiant).first()
    groupes = etudiant.groupesArchive.all()

    request.session['archive'] = True

    if 'desarchiver' in request.POST:
            groupe_archive_id = request.POST.get("group_id")
            groupe_archive = get_object_or_404(GroupeArchive, id=groupe_archive_id)

            groupe = groupe_archive.groupe
            etudiant.groupes.add(groupe)
            etudiant.groupesArchive.remove(groupe_archive)


    groupes_data = []
    for groupe in groupes:
        total_taches = groupe.taches_archive.count()
        taches_terminees = groupe.taches_archive.filter(status="Terminé").count()
        progression = (taches_terminees / total_taches * 100) if total_taches > 0 else 0

        groupes_data.append({
            "groupe": groupe,
            "progression": int(progression) 
        })
    
    return render(request, 'singleSections/groupesArchive.html', {"groupes_data": groupes_data})
    
def calender_home(request):
    if request.session.get('user_type') != 'etudiant': return redirect('login')
    if request.method == 'POST':
        id_etudiant = request.session.get('user_id')
        etudiant = Etudiant.objects.filter(id=id_etudiant).first()

        title = request.POST.get('title')
        category = request.POST.get('event-level')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        if 'ajouter' in request.POST:
            data = Event(title=title, category=category, start_date=start_date, end_date=end_date, etudiant=etudiant)
            data.save()

        elif 'modifier' in request.POST:
            event_id = request.POST.get('event_id') 
            event = get_object_or_404(Event, id=event_id)  
            event.title = title
            event.category = category
            event.start_date = start_date
            event.end_date = end_date
            event.save()

        elif 'supprimer' in request.POST:
            event_id = request.POST.get('event_id') 
            event = get_object_or_404(Event, id=event_id)  
            event.delete()

    return render(request, 'home/calender.html')

def projets(request, classe_id):
    if request.session.get('user_type') != 'etudiant': return redirect('login')
    classe = get_object_or_404(Classe, code_classe=classe_id)
    id_etudiant = request.session.get('user_id')
    etudiant = Etudiant.objects.filter(id=id_etudiant).first()
    
    if request.method == 'POST' and 'creer_groupe' in request.POST:
        nom_groupe = request.POST.get('nom_groupe')  
        selectedStudents = request.POST.get('selected-students', '')

        if selectedStudents.strip():  # Si la chaîne n’est pas vide ou espace
            try:
                student_ids = [int(id) for id in selectedStudents.split('-') if id.strip().isdigit()]
                selected_students = Etudiant.objects.filter(id__in=student_ids)
            except ValueError:
                # Gérer le cas d'une valeur incorrecte
                return HttpResponse("Liste d'étudiants invalide.", status=400)
        else:
            student_ids = []
            selected_students = []

        

        projet_id = request.POST.get('projet_id')
        projet = get_object_or_404(Project, id=projet_id)
        groupe = Groupe.objects.create(nom_groupe=nom_groupe, projet=projet, nbr_membre=4)

        # Ajouter l'étudiant créateur du groupe
        groupe.membres.add(etudiant)

        # Invitations
        notifications = [
            Notification(etudiant=etud, groupe=groupe) for etud in selected_students
        ]
        Notification.objects.bulk_create(notifications)

        # Instructions du projet
        for instruction in projet.instructions.all():
            InstructionStatus.objects.create(
                instruction=instruction,
                groupe=groupe, 
                est_termine=False,
                fichier_livrable=None
            )

    #  Projets associés à l'étudiant
    projets_associés = Project.objects.filter(
    groupe__membres=etudiant,
    code_classe=classe
)
    groupes_associes = Groupe.objects.filter(
    projet__code_classe=classe,
    membres=etudiant
).select_related('projet').order_by('projet__date_debut')


    # Projets de la classe où il n’est pas encore dans un groupe
    projets_non_associés = Project.objects.filter(
        code_classe=classe
    ).exclude(
        id__in=projets_associés
    )

    # Étudiants de la classe (pour affichage dans le formulaire)
    etudiants = classe.etudiants.all().exclude(id=etudiant.id)

        
    return render(request, 'singleSections/projet.html', {
    'projets_non_associés': projets_non_associés,
    'groupes_associes': groupes_associes,  # ✅ nom sans espace
    'etudiants': etudiants
})

# def projets(request, classe_id):
#     if request.session.get('user_type') != 'etudiant': return redirect('login')
#     classe = get_object_or_404(Classe, code_classe=classe_id)
#     id_etudiant = request.session.get('user_id')
#     etudiant = Etudiant.objects.filter(id=id_etudiant).first()
    
#     if request.method == 'POST' and 'creer_groupe' in request.POST:
#         nom_groupe = request.POST.get('nom_groupe')  
#         selectedStudents = request.POST.get('selected-students', '')

#         if selectedStudents.strip():  # Si la chaîne n’est pas vide ou espace
#             try:
#                 student_ids = [int(id) for id in selectedStudents.split('-') if id.strip().isdigit()]
#                 selected_students = Etudiant.objects.filter(id__in=student_ids)
#             except ValueError:
#                 # Gérer le cas d'une valeur incorrecte
#                 return HttpResponse("Liste d'étudiants invalide.", status=400)
#         else:
#             student_ids = []
#             selected_students = []

        

#         projet_id = request.POST.get('projet_id')
#         projet = get_object_or_404(Project, id=projet_id)
#         groupe = Groupe.objects.create(nom_groupe=nom_groupe, projet=projet, nbr_membre=4)

#         # Ajouter l'étudiant créateur du groupe
#         groupe.membres.add(etudiant)

#         # Invitations
#         notifications = [
#             Notification(etudiant=etud, groupe=groupe) for etud in selected_students
#         ]
#         Notification.objects.bulk_create(notifications)

#         # Instructions du projet
#         for instruction in projet.instructions.all():
#             InstructionStatus.objects.create(
#                 instruction=instruction,
#                 groupe=groupe, 
#                 est_termine=False,
#                 fichier_livrable=None
#             )

#     #  Projets associés à l'étudiant
#     projets_associés = Project.objects.filter(
#     groupe__membres=etudiant,
#     code_classe=classe
# )
#     groupes_associes = Groupe.objects.filter(
#     projet__code_classe=classe,
#     membres=etudiant
# ).select_related('projet').order_by('projet__date_debut')


#     # Projets de la classe où il n’est pas encore dans un groupe
#     projets_non_associés = Project.objects.filter(
#         code_classe=classe
#     ).exclude(
#         id__in=projets_associés
#     )

#     # Étudiants de la classe (pour affichage dans le formulaire)
#     etudiants = classe.etudiants.all().exclude(id=etudiant.id)

        
#     return render(request, 'singleSections/projet.html', {
#     'projets_non_associés': projets_non_associés,
#     'groupes_associes': groupes_associes,  # ✅ nom sans espace
#     'etudiants': etudiants
# })


  
# def profil(request):
#     if request.session.get('user_type') != 'etudiant': return redirect('login')
#     id_etudiant = request.session.get('user_id')
#     etudiant = get_object_or_404(Etudiant, id=id_etudiant)

#     if request.method == "POST":
#         nom = request.POST.get("nom")
#         prenom = request.POST.get("prenom")
#         photo = request.FILES.get("photo_profil")

#         # Mettre à jour les informations
#         if nom:
#             etudiant.nom = nom
#         if prenom:
#             etudiant.prenom = prenom
#         if photo:
#             # Supprimer l'ancienne photo si ce n'est pas la photo par défaut
#             if etudiant.photo_profil and etudiant.photo_profil.name != "images/profile.jpeg":
#                 default_storage.delete(etudiant.photo_profil.path)
#             etudiant.photo_profil = photo

#         etudiant.save()  # Enregistrer les modifications dans la base de données

#     nombre_classes = etudiant.classes.count()

#     return render(request, 'singleSections/profil.html', {
#         'etudiant': etudiant,
#         "nombre_classes": nombre_classes
#     })

def profil(request):
    if request.session.get('user_type') != 'etudiant': 
        return redirect('login')
    
    id_etudiant = request.session.get('user_id')
    etudiant = get_object_or_404(Etudiant, id=id_etudiant)

    est_archive = request.GET.get('archive', 'false').lower() == 'true'
    request.session['archive'] = est_archive

    if request.method == "POST":
        # Gestion du formulaire (existant)
        nom = request.POST.get("nom")
        prenom = request.POST.get("prenom")
        photo = request.FILES.get("photo_profil")

        if nom:
            etudiant.nom = nom
        if prenom:
            etudiant.prenom = prenom
        if photo:
            if etudiant.photo_profil and etudiant.photo_profil.name != "images/profile.jpeg":
                default_storage.delete(etudiant.photo_profil.path)
            etudiant.photo_profil = photo
        etudiant.save()

    # 1. Compter les classes non archivées
    #  Récupérer toutes les classes NON archivées pour cet étudiant via la table intermédiaire
    relations = EtudiantClasse.objects.filter(etudiant=etudiant, is_archived=False).select_related('classe')
    classes_non_archivees = [rel.classe for rel in relations]
    nombre_classes = len(classes_non_archivees)

    # 2. Calculer les projets terminés et non terminés
    projets_termines = 0
    projets_non_termines = 0

    # Récupérer tous les projets des classes non archivées
    projets = Project.objects.filter(
        code_classe__in=classes_non_archivees
    ).select_related('code_classe').prefetch_related(
        'instructions',
        'instructions__statuses'
    )

    for projet in projets:
        # Exclure les projets des classes archivées (double vérification)
        if projet.code_classe.is_archived:
            continue
            
        instructions = projet.instructions.all()
        
        # Cas spécial: pas d'instructions
        if not instructions.exists():
            projets_non_termines += 1
            continue
            
        # Vérifier l'état des instructions pour les groupes de l'étudiant
        groupes_etudiant = etudiant.groupes.all()

        if not groupes_etudiant.exists():
            # Si l'étudiant n'a pas de groupe dans ce projet
            projets_non_termines += 1
            continue
            
        projet_termine = True
        for groupe in groupes_etudiant:
            for instruction in instructions:
                try:
                    status = InstructionStatus.objects.get(
                        instruction=instruction,
                        groupe=groupe
                    )
                    if not status.est_termine:
                        projet_termine = False
                        break
                except InstructionStatus.DoesNotExist:
                    projet_termine = False
                    break
                
            if not projet_termine:
                break
                
        if projet_termine:
            projets_termines += 1
        else:
            projets_non_termines += 1

    return render(request, 'singleSections/profil.html', {
        'etudiant': etudiant,
        'nombre_classes': nombre_classes,
        'projets_termines': projets_termines,
        'projets_non_termines': projets_non_termines
    })

def get_events(request):
    if request.session.get('user_type') != 'etudiant': return redirect('login')
    id_etudiant = request.session.get('user_id')
    etudiant = Etudiant.objects.get(id=id_etudiant)
    events = Event.objects.filter(etudiant=etudiant)
    event_list = []

    for event in events:
        event_list.append({
            "id": event.id,
            "title": event.title,
            "start": event.start_date.strftime("%Y-%m-%d"),
            "end": event.end_date.strftime("%Y-%m-%d"),
            "extendedProps": {"calendar": event.category},  # Utilisé pour la couleur ou le type d'événement
        })

    return JsonResponse(event_list, safe=False)

# Configuration du logging pour débugger
logger = logging.getLogger(__name__)

def lancer_meet(request, groupe_id):
    logger.info(f"Tentative de lancement du meet pour le groupe {groupe_id}")
    
    try:
        # Verify session
        etudiant_id = request.session.get('user_id')
        if not etudiant_id:
            logger.error("Aucun utilisateur connecté")
            return JsonResponse({
                'success': False,
                'message': 'Session utilisateur invalide'
            }, status=401)

        groupe = get_object_or_404(Groupe, id=groupe_id)
        etudiant = get_object_or_404(Etudiant, id=etudiant_id)
        
        # Generate meet link
        base_url = f"https://meet.jit.si/groupe-{groupe.id}-{slugify(groupe.nom_groupe)}"
        user_params = {
            'userInfo.displayName': f"{etudiant.prenom} {etudiant.nom}",
            'userInfo.email': etudiant.email_etudiant,
            'config.prejoinPageEnabled': 'false',
        }
        query_string = urlencode(user_params)
        meet_link = f"{base_url}?{query_string}"
        
        # Save to database
        groupe.meet_link = meet_link
        groupe.save()
        
        logger.info(f"Meet créé avec succès: {meet_link}")
        
        return JsonResponse({
            'success': True,
            'meet_link': meet_link,
            'message': 'Meet lancé avec succès'
        })
        
    except Exception as e:
        logger.exception(f"Erreur lors du lancement du meet: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)

def terminer_meet(request, groupe_id):
    logger.info(f"Tentative de fermeture du meet pour le groupe {groupe_id}")
    
    try:
        groupe = get_object_or_404(Groupe, id=groupe_id)
        groupe.meet_link = ""
        groupe.save()
        logger.info("Meet terminé et lien supprimé")
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Meet terminé'
            })
        
        return redirect('chat')
        
    except Exception as e:
        logger.error(f"Erreur lors de la fermeture du meet: {str(e)}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': f'Erreur: {str(e)}'
            }, status=500)
        return redirect('chat')






















