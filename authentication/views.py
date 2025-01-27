from django.shortcuts import render,redirect
from django.contrib.auth import login
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from base_de_donnee.models import Etudiant,Professeur

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

                    if remember_me:  
                        request.session.set_expiry(None)  
                    else:  
                        request.session.set_expiry(0) 

                    professeur.last_login = timezone.now()  
                    professeur.save()

                    print("connecté en tant que professeur")
                    return render(request, 'authentification/message.html', {'message': 'Login successful! Welcome to the platform.'})
                    

        elif email.endswith('-etu@etu.univh2c.ma'):
                etudiant = Etudiant.objects.authenticate(email=email, password=password)
                
                if etudiant is None:
                    return render(request, 'authentification/message.html', {'message': 'the student is not exist'})
                
                elif etudiant == 'incorrect_password':
                    return render(request, 'authentification/message.html', {'message': 'the password is incorrect'})
                
                else:
                    login(request, etudiant)

                    if remember_me:  
                        request.session.set_expiry(None)  
                    else:  
                        request.session.set_expiry(0) 
                    
                    etudiant.last_login = timezone.now()  
                    etudiant.save()
                    return render(request, 'authentification/message.html', {'message': 'Login successful! Welcome to the platform.'})
                
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
            return render(request, 'authentification/message.html', {'message': 'The passwords do not match'})
        
        # Vérifier si l'email est déjà pris
        if Professeur.objects.filter(EMAIL=email).exists() or Etudiant.objects.filter(EMAIL_ETUDIANT=email).exists():
            return render(request, 'authentification/message.html', {'message': 'This email is already taken'})

        # Sauvegarder l'utilisateur
        if email.endswith('@enset-media.ac.ma'):
            professeur = Professeur(
                DEPARTEMENT=departement,
                SPECIALITE=departement,
                EMAIL=email,
                PASSWORD=make_password(password),
                NOM=nom,
                PRENOM=prenom,
                last_login=None  # Le champ peut être laissé à None lors de l'inscription
            )
            professeur.save()
            return render(request, 'authentification/message.html', {'message': 'Welcome Professor!'})

        elif email.endswith('-etu@etu.univh2c.ma'):
            etudiant = Etudiant(
                FILIERE=filiere,
                EMAIL_ETUDIANT=email,
                PASSWORD=make_password(password),
                NOM=nom,
                PRENOM=prenom,
                DEPARTEMENT=departement,
                last_login=None  # Le champ peut être laissé à None lors de l'inscription
            )
            etudiant.save()
            return render(request, 'authentification/message.html', {'message': 'Welcome Student!'})
        else:
            return render(request, 'authentification/message.html', {'message': 'Invalid email format. Use "@enset-media.ac.ma" for professors or "-etu@etu.univh2c.ma" for students.'})

    return render(request, 'authentification/signup.html')
