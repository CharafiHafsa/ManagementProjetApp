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
import time







def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')

        if email.endswith('@enset-media.ac.ma'):
                professeur = Professeur.objects.authenticate(email=email, password=password)
                if professeur is  None:
                    return render(request, 'authentification/message.html', {'message': 'the professor is not exist'})
                elif professeur == 'incorrect_password':
                    return render(request, 'authentification/message.html', {'message': 'the password is incorrect'})
                else:
                    if professeur.is_verified:
                            login(request, professeur)

                            request.session['user_type'] = 'professeur'
                            request.session['user_id'] = professeur.id  

                            if remember_me:  
                                request.session.set_expiry(None)  
                            else:  
                                request.session.set_expiry(0) 

                            professeur.last_login = timezone.now()  
                            professeur.save()

                            return render(request, 'authentification/message.html', {'message': 'Login successful! Welcome to the platform'})
                    else:
                        return render(request, 'authentification/message.html', {'message': 'Le compte n\'est pas activé'})
                        

        elif email.endswith('-etu@etu.univh2c.ma'):
                etudiant = Etudiant.objects.authenticate(email=email, password=password)

                if etudiant is None:
                    return render(request, 'authentification/message.html', {'message': 'the student is not exist'})
                
                elif etudiant == 'incorrect_password':
                    return render(request, 'authentification/message.html', {'message': 'the password is incorrect'})
                
                else:
                    if etudiant.is_verified:

                        login(request, etudiant)

                        request.session['user_type'] = 'etudiant'
                        request.session['user_id'] = etudiant.id  

                        if remember_me:  
                            request.session.set_expiry(None)  
                        else:  
                            request.session.set_expiry(0) 
                        
                        etudiant.last_login = timezone.now()  
                        etudiant.save()
                        return render(request, 'authentification/message.html', {'message': 'Login successful! Welcome to the platform'})
                    else:
                       return render(request, 'authentification/message.html', {'message': 'Le compte n\'est pas activé'})
        else:
            return render(request, 'authentification/message.html', {'message': "Please enter a valid email. Professors should use '@enset-media.ac.ma' and students should use '-etu@etu.univh2c.ma'"})
    return render(request, 'authentification/login.html')

def signup_view(request):
    user = None
    id_utilisateur = request.GET.get('uid')
    token = request.GET.get('token')

    if id_utilisateur and token:
        try:
            id = force_str(urlsafe_base64_decode(id_utilisateur))
            user = Professeur.objects.filter(pk=id).first() or Etudiant.objects.filter(pk=id).first()
        except (TypeError, ValueError, OverflowError):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_verified = True
            user.save()
            return render(request, 'authentification/message.html', {'message': 'Vérification réussie'})
        else:
            return render(request, 'authentification/message.html', {'message': 'Échec de la vérification'})

    
    if request.method == 'POST':
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        filiere = request.POST.get('filiere')
        departement = request.POST.get('departement')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Vérifier les mots de passe
        if password != confirm_password:
            return render(request, 'authentification/message.html', {'message': 'the password is not the same'})

        # Vérifier si l'email existe déjà
        if Professeur.objects.filter(email=email, is_verified=True).exists() or Etudiant.objects.filter(email_etudiant=email, is_verified=True).exists():
            return render(request, 'authentification/message.html', {'message': 'This email is already taken'})

        current_site = get_current_site(request)

        # Enregistrement des Professeurs
        if email.endswith('@enset-media.ac.ma'):
            professeur = Professeur(
                departement=departement,
                specialite=departement,
                email=email,
                password=make_password(password),
                nom=nom,
                prenom=prenom,
                last_login=None,
                is_verified=False
            )
            professeur.save()

            uid = urlsafe_base64_encode(force_bytes(professeur.pk))
            token = default_token_generator.make_token(professeur)
            verification_link = f"http://{current_site.domain}/etu/signup/?uid={uid}&token={token}"

            html_message = f"""
                <html>
                    <body>
                        <h1>Confirmez votre e-mail</h1>
                        <p>Pour confirmer votre compte, cliquez sur le bouton ci-dessous :</p>
                        <a href="{verification_link}">
                            <button style="padding: 10px 15px; font-size: 16px; color: white; background-color: #007BFF; border-radius: 5px; border: none; cursor: pointer;">
                                Confirmer mon compte
                            </button>
                        </a>
                    </body>
                </html>
            """

            send_mail(
                "Confirmez votre compte",
                "",
                "najibimane093@gmail.com",
                [email],
                fail_silently=False,
                html_message=html_message,
            )

        # Enregistrement des Étudiants
        elif email.endswith('-etu@etu.univh2c.ma'):
            etudiant = Etudiant(
                filiere=filiere,
                email_etudiant=email,
                password=make_password(password),
                nom=nom,
                prenom=prenom,
                departement=departement,
                last_login=None,
                is_verified=False
            )
            etudiant.save()

            uid = urlsafe_base64_encode(force_bytes(etudiant.pk))
            token = default_token_generator.make_token(etudiant)
            verification_link = f"http://{current_site.domain}/etu/signup/?uid={uid}&token={token}"

            html_message = f"""
                <html>
                    <body>
                        <h1>Confirmez votre e-mail</h1>
                        <p>Pour confirmer votre compte, cliquez sur le bouton ci-dessous :</p>
                        <a href="{verification_link}">
                            <button style="padding: 10px 15px; font-size: 16px; color: white; background-color: #007BFF; border-radius: 5px; border: none; cursor: pointer;">
                                Confirmer mon compte
                            </button>
                        </a>
                    </body>
                </html>
            """

            send_mail(
                "Confirmez votre compte",
                "",
                "najibimane093@gmail.com",
                [email],
                fail_silently=False,
                html_message=html_message,
            )
            return render(request, 'authentification/message.html', {'message': 'Your email has been sent successfully'})
        else:
            return render(request, 'authentification/message.html', {'message': 'Invalid email format. Use "@enset-media.ac.ma" for professors or "-etu@etu.univh2c.ma" for students'})

    return render(request, 'authentification/signup.html')

def forget_password(request):
    if request.method == 'POST':
        email = request.POST.get('email_forgot')
        
        request.session['reset_email'] = email

        reset_link = f"http://127.0.0.1:8000/update_password/?id={uuid.uuid4()}"

        if email.endswith('-etu@etu.univh2c.ma'):
            etudiant = Etudiant.objects.filter(EMAIL_ETUDIANT=email).first()
            if etudiant is not None:

                html_message = f"""
                                    <html>
                                        <body>
                                            <h1>Réinitialisation du mot de passe</h1>
                                            <p>We received a request to reset your password. If you made this request, please click the button below to reset your password:</p>
                                            <a href="{reset_link}">
                                                <button type="button" style="padding: 10px 15px; font-size: 16px; color: white; background-color: #007BFF; border-radius: 5px; border: none; cursor: pointer;">
                                                    Réinitialiser le mot de passe
                                                </button>
                                            </a>
                                        </body>
                                    </html>
                                """

                send_mail(
                    "Update password",
                    "",  
                    "votre_email@gmail.com",
                    [email],
                    fail_silently=False,
                    html_message=html_message,
                )
                return render(request, 'authentification/message.html', {'message': 'Your email has been sent successfully'})
            else:
                return render(request, 'authentification/message.html', {'message': 'the student is not exist'})

        elif email.endswith('@enset-media.ac.ma'):
            professeur = Professeur.objects.filter(EMAIL=email).first()
            if professeur is not None:
                html_message = f"""
                        <html>
                            <body>
                                <h1>Réinitialisation du mot de passe</h1>
                                <p>We received a request to reset your password. If you made this request, please click the button below to reset your password:</p>
                                <a href="{reset_link}">
                                    <button type="button" style="padding: 10px 15px; font-size: 16px; color: white; background-color: #007BFF; border-radius: 5px; border: none; cursor: pointer;">
                                        Réinitialiser le mot de passe
                                    </button>
                                </a>
                            </body>
                        </html>
                    """
                send_mail(
                    "Update password",
                    "",  
                    "votre_email@gmail.com",
                    [email],
                    fail_silently=False,
                    html_message=html_message,
                )
                return render(request, 'authentification/message.html', {'message': 'Your email has been sent successfully'})
            else:
                return render(request, 'authentification/message.html', {'message': 'the professor is not exist'})

        else:
            return render(request, 'authentification/message.html', {'message': 'Invalid email format'})

    return render(request, 'authentification/forget_password.html')

def update_password(request):
    email = request.session.get('reset_email')

    if request.method == 'POST':
        newpassword = request.POST.get('new_password')
        confirmed_new_password = request.POST.get('confirmed_new_password')

        if newpassword != confirmed_new_password:
            return render(request, 'authentification/message.html', {'message': 'the two password is not the same'})
        
        
        if email.endswith('-etu@etu.univh2c.ma'):
             etudiant = Etudiant.objects.filter(EMAIL_ETUDIANT=email).first()
             etudiant.PASSWORD = make_password(newpassword)
             etudiant.save()
             return render(request, 'authentification/message.html', {'message': 'Your password has been successfully updated'})
        elif email.endswith('@enset-media.ac.ma'):
            professeur = Professeur.objects.filter(EMAIL=email).first()
            professeur.PASSWORD = make_password(newpassword)
            professeur.save()
            return render(request, 'authentification/message.html', {'message': 'Your password has been successfully updated'})


         
    return render(request, 'authentification/update_password.html')

def logout_user(request):
    logout(request)
    request.session.flush()
    update_time_counter(request)
    return redirect('login')


def detailles(request):
    return render(request, 'workSpace/detailles.html')


def dashBoard_ws(request):

    groupe_id = request.session.get('groupe_id', None)
    groupe = get_object_or_404(Groupe, id=groupe_id)
    taches_groupe = Taches.objects.filter(groupe=groupe)
    nb_taches_terminees = taches_groupe.filter(status="Terminé").count()
    nb_taches_en_cours = taches_groupe.filter(deadline__gte=timezone.now().date(),status="En cours").count()
    nb_taches_retard = taches_groupe.filter(deadline__lt=timezone.now().date(), status="En cours").count()
    nb_tache_total = taches_groupe.count()
    
    if groupe.projet:
        projet = groupe.projet

        # Récupérer la date actuelle
        date_actuelle = date.today()

        # Calculer la durée totale du projet (différence entre la date de début et la date de fin)
        duree_totale = projet.date_fin - projet.date_debut

        # Calculer la durée écoulée (différence entre la date actuelle et la date de début)
        if date_actuelle > projet.date_fin:
            pourcentage = 100
        else:
            temps_ecoule = date_actuelle - projet.date_debut
            pourcentage = (temps_ecoule.days / duree_totale.days) * 100

        # les jours restants
        jours_restants = (projet.date_fin - date_actuelle).days

        # Afficher le pourcentage dans le contexte de la vue
        return render(request, 'workSpace/dashBoard.html', {
            'projet': projet, 
            'pourcentage': int(pourcentage), 
            'jours_restants': jours_restants,
            'groupe' : groupe,
            'nb_tache_termine' : nb_taches_terminees,
            'nb_tache_en_cours':nb_taches_en_cours , 
            'nb_taches_retard' : nb_taches_retard,
            'nb_tache_total':nb_tache_total,
            'nb_tache_non_realisé' : nb_taches_en_cours + nb_taches_retard
            })
    return render(request, 'workSpace/dashBoard.html')

def dashBoard_home(request):
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

def todo_home(request):
    id_etudiant = request.session.get('user_id')
    etudiant = Etudiant.objects.filter(id=id_etudiant).first()
    # Prmière page affiché: checker les deadlines et envoyer des rappels
    jours_avant_deadline = 1
    nombre_de_lettres = 10
    today = date.today()
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
    id_etudiant = request.session.get('user_id')
    today = datetime.date.today()
    # Récupérer l'ID du groupe depuis la session
    groupe_id = request.session.get('groupe_id', None)
    if request.session.get('archive') == False: 
        groupe = get_object_or_404(Groupe, id=groupe_id)
    else:
        groupe = get_object_or_404(GroupeArchive, id=groupe_id)
    
    if request.method == 'POST' :
        print(2)
        # SUPPRIMER
        if 'delete' in request.POST:
            id_tache = request.POST.get('id_tache')
            tache = get_object_or_404(Taches, id=id_tache)
            tache.delete()

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
        etudiants=Etudiant.objects.filter(groupes=groupe).exclude(id=id_etudiant)
    else:
        taches = Taches.objects.filter(groupeArchive=groupe)
        etudiants=Etudiant.objects.filter(groupesArchive=groupe).exclude(id=id_etudiant)

    archive = request.session.get('archive')
    return render(request, 'workSpace/todo.html', {'taches':taches,'etudiants':etudiants, 'groupe_id':groupe_id, 'today':today.isoformat(), 'archive':archive})

def ws_reception(request, groupe_id):
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
    # Récupérer l'ID du groupe depuis la session
    print("chat: ", request.session.get('groupe_id', None))
    groupe_id = request.session.get('groupe_id', None)

    # groupe_id = request.GET.get('groupe_id', 1)  
    if groupe_id:
        groupe = Groupe.objects.get(id=groupe_id)
        messages = Message.objects.filter(groupe=groupe).order_by("date_envoi")
        return render(request, 'workSpace/chat.html', {'messages': messages, 'groupe': groupe})
    else:
        return HttpResponse('Aucun groupe choisi.')   

def memberes(request):
    # Récupérer l'ID du groupe depuis la session
    groupe_id = request.session.get('groupe_id', None)
    if request.session.get('archive') == False: 
        etudiants = Etudiant.objects.filter(groupes=groupe_id)
    else:
        etudiants = Etudiant.objects.filter(groupesArchive=groupe_id)

    if request.method == "POST":
        if "delete" in request.POST:
            etudiant_id = request.POST.get("id_etudiant")
            etudiant = get_object_or_404(Etudiant, id=etudiant_id)

            if request.session.get('archive') == False: 
                etudiant.groupes.remove(groupe_id) 
            else:
                etudiant.groupesArchive.remove(groupe_id) 

            return render(request, 'workSpace/membres.html', {'etudiants': etudiants})
        if "btn-add" in request.POST: 
        # Récupération de l'email du formulaire
            email = request.POST.get("email") 
            try:
                etudiant = Etudiant.objects.get(email_etudiant=email)  
                if request.session.get('archive') == False: 
                    groupe = Groupe.objects.get(id=groupe_id) 
                    Notification.objects.create(etudiant=etudiant, groupe=groupe)
                
                return render(request, 'workSpace/membres.html', {
                    'etudiants': etudiants,
                    'success_message': "Invitation envoyée avec succès"
                })
            except Etudiant.DoesNotExist:
                return render(request, 'workSpace/membres.html', {
                    'etudiants': etudiants,
                    'error_message': "Cet email n'existe pas dans la base de données"
                })
    archive = request.session.get('archive')
    return render(request, 'workSpace/membres.html', {'etudiants': etudiants, 'archive':archive})

def ouvrir_doc(request):
    if request.method == "POST":
        file_url = request.POST.get('file_path')

        if not file_url or not file_url.startswith(settings.MEDIA_URL):
            raise Http404("Fichier introuvable")

        file_path = os.path.join(settings.MEDIA_ROOT, file_url[len(settings.MEDIA_URL):])

        if not os.path.exists(file_path):
            raise Http404("Fichier introuvable sur le serveur")

        return FileResponse(open(file_path, 'rb'), content_type='application/octet-stream')

    raise Http404("Méthode non autorisée")

def documents(request):
    groupe_instance = Groupe.objects.get(id=request.session.get('groupe_id'))
    etu = Etudiant.objects.get(id=request.session.get('user_id'))

    if request.method == "POST":
        file = request.FILES.get("file")

        if not file:
            return JsonResponse({"success": False, "error": "Aucun fichier sélectionné"}, status=400)

        document = Document(title=os.path.splitext(file.name)[0], file=file, groupe=groupe_instance, etudiant=etu)
        document.save()

        return JsonResponse({"success": True, "id": document.id,"title": document.title, "file_url": document.file.url})  

    return render(request, 'workSpace/documents.html', {'doc': Document.objects.filter(groupe=groupe_instance)})


# def documents(request):

#     if request.session.get('archive') == False: 
#         groupe_instance = Groupe.objects.get(id=request.session.get('groupe_id'))
#     else:
#         groupe_instance = GroupeArchive.objects.get(id=request.session.get('groupe_id'))

#     if request.method == "POST":
#         file = request.FILES.get("file")
#         if not file:
#             return JsonResponse({"success": False, "error": "Aucun fichier sélectionné"}, status=400)
        
#         if request.session.get('archive') == False: 
#             document = Document(title=os.path.splitext(file.name)[0], file=file, groupe=groupe_instance)
#         else:
#             document = Document(title=os.path.splitext(file.name)[0], file=file, groupeArchive=groupe_instance)

#         document.save()
#         return JsonResponse({"success": True, "file_url": document.file.url})


#     if request.session.get('archive') == False: 
#         return render(request, 'workSpace/documents.html', {'doc': Document.objects.filter(groupe=groupe_instance), 'archive':False})
#     else:
#         return render(request, 'workSpace/documents.html', {'doc': Document.objects.filter(groupeArchive=groupe_instance), 'archive':True})

def suppDoc(request):
    if request.method == 'POST' and 'delete' in request.POST:

        document_id = request.POST.get('document_id')
        
        if document_id:
            document = get_object_or_404(Document, id=document_id)
            document.delete()
            return redirect('documents')
        return HttpResponse("Requête invalide", status=400)
        
def Quitter_Modifier(request):
    print("I am here")
    if request.method == 'POST':
        if 'delete_groupe' in request.POST:
            groupe_id = request.POST.get('id_groupe_quitter')
            print("GroupeId delete : ",groupe_id)
            if groupe_id:
                groupe = get_object_or_404(Groupe,id=groupe_id)
                groupe.delete()
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
    try:
        # Récupérer l'étudiant et le groupe depuis la session
        etudiant_id = request.session.get('user_id')
        groupe_id = request.session.get('groupe_id')

        if not etudiant_id or not groupe_id:
            return JsonResponse({'error': 'Identifiants utilisateur ou groupe manquants.'}, status=400)

        etudiant = Etudiant.objects.filter(id=etudiant_id).first()
        groupe = Groupe.objects.filter(id=groupe_id).first()

        if not etudiant or not groupe:
            return JsonResponse({'error': 'Étudiant ou groupe non trouvé.'}, status=400)

        # Récupérer tous les sujets associés au groupe
        sujets = Sujet.objects.filter(groupe=groupe)

        # Vérifier si un sujet existe déjà pour l'étudiant
        sujet = None
        sujet_id = request.POST.get('subject_id')
        if sujet_id:
            sujet = Sujet.objects.filter(id=sujet_id).first()

        # Gérer la requête POST pour un nouveau message
        if request.method == 'POST':
            user_message = request.POST.get('message', '').strip()

            if not user_message:
                return JsonResponse({'error': 'Le message ne peut pas être vide.'}, status=400)

            # Créer un nouveau sujet si aucun n'existe
            if not sujet:
                sujet = Sujet.objects.create(
                    titre=f"Conversation sur : {user_message[:30]}...",
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

            return JsonResponse({'response': formatted_response})

        # Afficher la page avec les sujets disponibles
        return render(request, 'WorkSpace/chatbot.html', {'sujets': sujets})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_conversation(request, sujet_id):
    try:
        sujet = Sujet.objects.filter(id=sujet_id).first()

        if not sujet:
            return JsonResponse({'error': 'Sujet non trouvé.'}, status=404)

        messages = ChatMessage.objects.filter(sujet=sujet).order_by('id')

        conversation_data = [
            {'contenu': message.contenu, 'etudiant': message.etudiant.nom if message.etudiant else 'Chatbot'}
            for message in messages
        ]

        return JsonResponse({'messages': conversation_data})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def classes(request): 
    id_etudiant = request.session.get('user_id')
    etudiant = Etudiant.objects.filter(id=id_etudiant).first()
    classes_data = etudiant.classes.all()

    context = {
        'classes': classes_data
    }

    return render(request, 'singleSections/classes.html', context)

def notifications(request):
    id_etudiant = request.session.get('user_id')
    etudiant = Etudiant.objects.filter(id=id_etudiant).first()
    notifications = Notification.objects.filter(etudiant=etudiant)
    taches_proches = request.session.get('taches_proches', [])
    taches_depassees = request.session.get('taches_depassees', [])

    if request.method == 'POST' :
        # suprimer une notification
        if 'delete' in request.POST:
            id_notification = request.POST.get('id_notification')
            notification  = get_object_or_404(Notification, id=id_notification )
            notification .delete()
        # accepter une invitation
        if 'accepter' in request.POST:
            id_notification = request.POST.get('id_notification')
            notification  = get_object_or_404(Notification, id=id_notification )
            groupe=notification.groupe
            groupe.membres.add(etudiant)  
            groupe.nbr_membre += 1  
            groupe.save()  
            notification .delete()



    return render(request, 'singleSections/notifications.html',  {'taches_proches':taches_proches, 'taches_depassees':taches_depassees , 'notifications':notifications})

def groupes(request):
    id_etudiant = request.session.get('user_id')
    etudiant = Etudiant.objects.filter(id=id_etudiant).first()
    groupes = etudiant.groupes.all()

    
    if request.method == "POST" :
        # archiver le groupe -------------------------------------------------
        if 'archiver' in request.POST:
            group_id = request.POST.get("group_id")
            groupe = get_object_or_404(Groupe, id=group_id)

            with transaction.atomic():  # Garantit que tout est exécuté sans erreur
                # 1. Créer une instance dans GroupeArchive
                groupe_archive = GroupeArchive.objects.create(
                    nom_groupe=groupe.nom_groupe,
                    nbr_membre=groupe.nbr_membre,
                    projet=groupe.projet
                )

                # 2. Mettre à jour toutes les relations :

                # Taches → groupeArchive
                for tache in groupe.taches.all():
                    tache.groupe = None
                    tache.groupeArchive = groupe_archive
                    tache.save()

                # Documents → groupeArchive
                for document in groupe.documents.all():
                    document.groupe = None
                    document.groupeArchive = groupe_archive
                    document.save()

                # Notifications → groupeArchive
                for notification in groupe.notifications.all():
                    notification.groupe = None
                    notification.groupeArchive = groupe_archive
                    notification.save()

                # Mettre à jour les étudiants (ManyToMany)
                for etudiant in groupe.membres.all():
                    etudiant.groupes.remove(groupe)  # Retirer du groupe normal
                    etudiant.groupesArchive.add(groupe_archive)  # Ajouter à l'archive

                # 3. Supprimer le groupe original
                groupe.delete()

        else: # créer un groupe -------------------------------------------------
            
            nom_groupe = request.POST.get("nom_groupe")
            # Récupérer les emails sous forme de liste
            emails = request.POST.get("emails", "").split(",")
            # Créer le groupe
            groupe = Groupe.objects.create(nom_groupe=nom_groupe, nbr_membre=len(emails) + 1)
            groupe.membres.add(etudiant)
            erreurs = []
            
            # Vérifier chaque email et créer les notifications
            for email in emails:
                etudiant_invite = Etudiant.objects.filter(email_etudiant=email).first()
                if etudiant_invite:
                    Notification.objects.create(etudiant=etudiant_invite, groupe=groupe)
                else:
                    erreurs.append(f"L'email {email} n'existe pas dans la base de données.")
            if erreurs:
                messages.error(request, "\n".join(erreurs))
            else:
                messages.success(request, "Groupe créé avec succès !")
    
    
    groupes_data = []
    for groupe in groupes:
        total_taches = groupe.taches.count()
        taches_terminees = groupe.taches.filter(status="Terminé").count()
        progression = (taches_terminees / total_taches * 100) if total_taches > 0 else 0

        groupes_data.append({
            "groupe": groupe,
            "progression": int(progression) 
        })
    
    return render(request, 'singleSections/groupes.html', {"groupes_data": groupes_data})
    
def groupes_archive(request):
    id_etudiant = request.session.get('user_id')
    etudiant = Etudiant.objects.filter(id=id_etudiant).first()
    groupes = etudiant.groupesArchive.all()

    if 'desarchiver' in request.POST:
        groupe_archive_id = request.POST.get("group_id")
        groupe_archive = get_object_or_404(GroupeArchive, id=groupe_archive_id)

        with transaction.atomic():  # Garantit l'exécution sans erreur
            # 1. Créer une nouvelle instance de Groupe
            groupe = Groupe.objects.create(
                nom_groupe=groupe_archive.nom_groupe,
                nbr_membre=groupe_archive.nbr_membre,
                projet=groupe_archive.projet
            )

            # 2. Mettre à jour toutes les relations :

            # Taches → Groupe
            for tache in groupe_archive.taches_archive.all():
                tache.groupeArchive = None
                tache.groupe = groupe
                tache.save()

            # Documents → Groupe
            for document in groupe_archive.documents_archive.all():
                document.groupeArchive = None
                document.groupe = groupe
                document.save()

            # Notifications → Groupe
            for notification in groupe_archive.notifications_archive.all():
                notification.groupeArchive = None
                notification.groupe = groupe
                notification.save()

            # Mettre à jour les étudiants (ManyToMany)
            for etudiant in groupe_archive.membres.all():
                etudiant.groupesArchive.remove(groupe_archive)  # Retirer du groupe archivé
                etudiant.groupes.add(groupe)  # Ajouter au nouveau groupe

            # 3. Supprimer le groupe archivé
            groupe_archive.delete()


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
    if request.method == 'POST':
        id_etudiant = request.session.get('user_id')
        etudiant = Etudiant.objects.filter(id=id_etudiant).first()
        if 'ajouter' in request.POST:
            title = request.POST.get('title')
            category = request.POST.get('event-level')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
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

            return render(request, 'home/calender.html', {'valeur_cachee': valeur_cachee})

    return render(request, 'home/calender.html')

def projets(request, classe_id):
    classe= get_object_or_404(Classe, code_classe=classe_id)
    id_etudiant = request.session.get('user_id')
    if request.method =='POST' :
        if 'creer_groupe' in request.POST:
            nom_groupe=request.POST.get('nom_groupe')  

            selectedStudents = request.POST.get('selected-students')
            # 1. Créer le groupe
            student_ids = [int(id) for id in selectedStudents.split('-')]
            selected_students = Etudiant.objects.filter(id__in=student_ids)
            projet_id=request.POST.get('projet_id')
            projet= get_object_or_404(Project, id= projet_id)
            groupe=Groupe.objects.create(nom_groupe=nom_groupe, projet=projet, nbr_membre=4,)

            # ajouter l'etudiant qui a créer le groupe au groupe
            etudiant = Etudiant.objects.get(id=id_etudiant)
            groupe.membres.add(etudiant)

            # Envoyer les invitations
            notifications = [
                Notification(etudiant=etudiant, groupe=groupe) for etudiant in selected_students
            ]
            Notification.objects.bulk_create(notifications)

            # creer les status des instruction:*

            # Récupérer toutes les instructions liées à ce projet
            instructions = projet.instructions.all()
            # Créer un statut pour chaque instruction du projet
            for instruction in instructions:
                InstructionStatus.objects.create(
                    instruction=instruction,
                    groupe=groupe,  # Associe le statut avec le groupe
                    est_termine=False,  # Par défaut, il n'est pas terminé
                    fichier_livrable=None  # Pas de fichier pour l'instant
                )

    etudiant = Etudiant.objects.filter(id=id_etudiant).first()
         
    etudiants = classe.etudiants.all().exclude(id=id_etudiant)

    projets_associés = Project.objects.filter(groupe__membres=etudiant).distinct()

    # 2. Projets liés aux classes de l'étudiant mais où il n'est pas dans un groupe
    projets_non_associés = Project.objects.filter(
        code_classe__etudiants=etudiant  # L'étudiant est dans la classe
    ).exclude(
        id__in=projets_associés   # Exclure les projets où il est déjà dans un groupe
    ).distinct()
        
    return render(request, 'singleSections/projet.html',{
        'projets_non_associés': projets_non_associés,
        'projets_associés':projets_associés,
        'etudiants':etudiants
        })

def profil(request):
    id_etudiant = request.session.get('user_id')
    etudiant = get_object_or_404(Etudiant, id=id_etudiant)

    if request.method == "POST":
        nom = request.POST.get("nom")
        prenom = request.POST.get("prenom")
        photo = request.FILES.get("photo_profil")

        # Mettre à jour les informations
        if nom:
            etudiant.nom = nom
        if prenom:
            etudiant.prenom = prenom
        if photo:
            # Supprimer l'ancienne photo si ce n'est pas la photo par défaut
            if etudiant.photo_profil and etudiant.photo_profil.name != "images/profile.jpeg":
                default_storage.delete(etudiant.photo_profil.path)
            etudiant.photo_profil = photo

        etudiant.save()  # Enregistrer les modifications dans la base de données

    nombre_classes = etudiant.classes.count()

    return render(request, 'singleSections/profil.html', {
        'etudiant': etudiant,
        "nombre_classes": nombre_classes
    })

def get_events(request):
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
























