from base_de_donnee.models import *
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render,redirect,get_object_or_404
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from django.contrib.auth import login
from django.utils import timezone
import uuid
import json



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
                    login(request, professeur)

                    request.session['user_type'] = 'professeur'
                    request.session['user_id'] = professeur.id  

                    if remember_me:  
                        request.session.set_expiry(None)  
                    else:  
                        request.session.set_expiry(0) 

                    professeur.last_login = timezone.now()  
                    professeur.save()

                    print("connecté en tant que professeur")
                    return render(request, 'authentification/message.html', {'message': 'Login successful! Welcome to the platform'})
                    

        elif email.endswith('-etu@etu.univh2c.ma'):
                etudiant = Etudiant.objects.authenticate(email=email, password=password)

                if etudiant is None:
                    return render(request, 'authentification/message.html', {'message': 'the student is not exist'})
                
                elif etudiant == 'incorrect_password':
                    return render(request, 'authentification/message.html', {'message': 'the password is incorrect'})
                
                else:
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
            return render(request, 'authentification/message.html', {'message': "Please enter a valid email. Professors should use '@enset-media.ac.ma' and students should use '-etu@etu.univh2c.ma'"})
    return render(request, 'authentification/login.html')

def signup_view(request):
    if request.method == 'POST':
        # Récupérer les données du formulaire
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        filiere = request.POST.get('filiere')
        departement = request.POST.get('departement')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Vérifier si les mots de passe correspondent
        if password != confirm_password:
            return render(request, 'authentification/message.html', {'message': 'the password is not the same'})
        
        # Vérifier si l'email est déjà pris
        if Professeur.objects.filter(email=email).exists() or Etudiant.objects.filter(email_etudiant=email).exists():
            return render(request, 'authentification/message.html', {'message': 'This email is already taken'})

        # Sauvegarder l'utilisateur
        if email.endswith('@enset-media.ac.ma'):
            professeur = Professeur(
                departement=departement,
                specialite=departement,
                email=email,
                password=make_password(password),
                nom=nom,
                prenom=prenom,
                last_login=None  
            )
            professeur.save()
            return render(request, 'authentification/message.html', {'message': 'welcome'})

        elif email.endswith('-etu@etu.univh2c.ma'):
            etudiant = Etudiant(
                filiere=filiere,
                email_etudiant=email,
                password=make_password(password),
                nom=nom,
                prenom=prenom,
                departement=departement,
                last_login=None
            )
            etudiant.save()
            return render(request, 'authentification/message.html', {'message': 'welcome'})
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



def chat(request):
    groupe_id = request.GET.get('groupe_id', 1)  
    groupe = Groupe.objects.get(id=groupe_id)
    messages = Message.objects.filter(groupe=groupe).order_by("date_envoi")
    return render(request, 'workSpace/chat.html', {'messages': messages, 'groupe': groupe})

def todo_ws(request):
    groupe_id=1
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
    return render(request, 'workSpace/todo.html', {'taches': taches,'etudiants':etudiants})

def todo_home(request):
    if request.method == 'POST' :
        if 'delete' in request.POST:
            id_tache = request.POST.get('id_tache')
            tache = get_object_or_404(Taches, id=id_tache)
            tache.delete()
        elif 'modifier' in request.POST: 
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


    taches = Taches.objects.all().select_related('groupe__projet')  

    return render(request, 'home/todo.html', {'taches': taches})

def classes(request): 
    classes_data = Classe.objects.all()  

    context = {
        'classes': classes_data
    }

    return render(request, 'singleSetions/classes.html', context)

def notifications(request):
    return render(request, 'singleSections/notifications.html')

def groupes(request):
    if request.method =='POST':
        groupe_id = request.POST.get('groupe_id')
        groupe = get_object_or_404(Groupe, id=groupe_id)
        taches = Taches.objects.filter(groupe=groupe)
        return render(request, 'todo.html', {'groupe': groupe, 'taches': taches})
    groupes = Groupe.objects.select_related("projet__code_classe").all()
    return render(request, 'singleSections/groupes.html', {'groupes': groupes})

def calender_home(request):
    if request.method == 'POST':
        if 'ajouter' in request.POST:
            title = request.POST.get('title')
            category = request.POST.get('event-level')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            data = Event(title=title, category=category, start_date=start_date, end_date=end_date)
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

def projets(request):
    return render(request, 'singleSections/projet.html')

def profil(request):
    return render(request, 'singleSections/profil.html')

def get_events(request):
    events = Event.objects.all()
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
