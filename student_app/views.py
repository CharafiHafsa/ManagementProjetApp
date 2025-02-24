
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode 
from django.http import JsonResponse ,HttpResponse,FileResponse,Http404
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.sites.shortcuts import get_current_site 
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.hashers import make_password
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import login,logout
from django.core.mail import send_mail
from base_de_donnee.models import *
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from datetime import date
import json
import uuid
import os




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
    request.session.flush()
    logout(request)
    return redirect('login')


def ws_reception(request, groupe_id):
    request.session['groupe_id'] = groupe_id
    return render(request, 'workSpace/ws_reception.html', {'groupe_id':groupe_id})

def dashBoard_home(request):
    id_etudiant = request.session.get('user_id')
    etudiant = Etudiant.objects.filter(id=id_etudiant).first()
    return render(request, 'home/dashBoard.html')

def get_taches_stats(request):
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
        taches_depassees = taches.filter(deadline__lt=datetime.date.today(), status="En cours").count()
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
    etudiants = Etudiant.objects.filter(groupes=groupe_id)
    if request.method == "POST":
        print('mmmm')
        if "delete" in request.POST:
            print('nnnnn')
            etudiant_id = request.POST.get("id_etudiant")
            etudiant = get_object_or_404(Etudiant, id=etudiant_id)
            print(etudiant_id, 'nnnnnnnnnnnnnnnn')

            # Suppression de l'étudiant du groupe (ou suppression complète si nécessaire)
            etudiant.groupes.remove(groupe_id)  # Si la relation est ManyToManyField
            # etudiant.delete()  # Si tu veux supprimer complètement l'étudiant

            return render(request, 'workSpace/membres.html', {'etudiants': etudiants})
        if "btn-add" in request.POST: 
        # Récupération de l'email du formulaire
            email = request.POST.get("email") 
            try:
                etudiant = Etudiant.objects.get(email_etudiant=email)  # Vérifie si l'étudiant existe
                groupe = Groupe.objects.get(id=groupe_id)  # Récupérer le groupe actuel
                Notification.objects.create(etudiant=etudiant, groupe=groupe) #creer la notification
                
                return render(request, 'workSpace/membres.html', {
                    'etudiants': etudiants,
                    'success_message': "Invitation envoyée avec succès"
                })
            except Etudiant.DoesNotExist:
                return render(request, 'workSpace/membres.html', {
                    'etudiants': etudiants,
                    'error_message': "Cet email n'existe pas dans la base de données"
                })

    return render(request, 'workSpace/membres.html', {'etudiants': etudiants})

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
    if request.method == "POST":
        file = request.FILES.get("file")

        if not file:
            return JsonResponse({"success": False, "error": "Aucun fichier sélectionné"}, status=400)
        
        document = Document(title=os.path.splitext(file.name)[0], file=file, groupe=groupe_instance)

        document.save()

        return JsonResponse({"success": True, "file_url": document.file.url})

    return render(request, 'workSpace/documents.html', {'doc': Document.objects.filter(groupe=groupe_instance)})

def todo_ws(request):
    today = datetime.date.today()
    # Récupérer l'ID du groupe depuis la session
    print("todo: ", request.session.get('groupe_id', None))
    groupe_id = request.session.get('groupe_id', None)

    groupe = get_object_or_404(Groupe, id=groupe_id)
    if request.method == 'POST' :
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

    
    taches = Taches.objects.filter(groupe=groupe)
    etudiants=Etudiant.objects.filter(groupes=groupe)
    return render(request, 'workSpace/todo.html', {'taches':taches,'etudiants':etudiants, 'groupe_id':groupe_id, 'today':today.isoformat()})

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
        deadline__lte=today + datetime.timedelta(days=jours_avant_deadline)  # Sélectionne uniquement les tâches dont la deadline est dans les prochains jours.
    )
    taches_depassees = Taches.objects.filter(
        etudiant_id=id_etudiant,
        status="En cours",
        deadline__lt=today
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

    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

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


    taches = Taches.objects.filter(etudiant=etudiant)

    return render(request, 'home/todo.html', {'taches': taches, 'nouvelle_notifications':nouvelle_notifications, 'today':today.isoformat()})

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
    return render(request, 'singleSections/notifications.html',  {'taches_proches':taches_proches, 'taches_depassees':taches_depassees , 'notifications':notifications})

def groupes(request):
    id_etudiant = request.session.get('user_id')
    etudiant = Etudiant.objects.filter(id=id_etudiant).first()
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

    if request.method == "POST":
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
    
    
    
    
    return render(request, 'singleSections/groupes.html', {"groupes_data": groupes_data})
    
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

    etudiant = Etudiant.objects.filter(id=id_etudiant).first()
         
    etudiants = classe.etudiants.all()

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
