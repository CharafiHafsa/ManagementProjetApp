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

            if professeur is None:
                messages.error(request, 'The professor does not exist.')
            elif professeur == 'incorrect_password':
                messages.error(request, 'The password is incorrect.')
            else:
                if professeur.is_verified:
                    login(request, professeur)
                    request.session['user_type'] = 'professeur'
                    request.session['user_id'] = professeur.id  
                    request.session['email'] = professeur.email

                    if remember_me:  
                        request.session.set_expiry(None)  
                    else:  
                        request.session.set_expiry(0) 

                    professeur.last_login = timezone.now()  
                    professeur.save()

                    messages.success(request, 'Login successful! Welcome Professeur.')
                    return redirect('prof_accueil')
                else:
                    messages.warning(request, 'Your account is not activated.')

        elif email.endswith('-etu@etu.univh2c.ma'):
            etudiant = Etudiant.objects.authenticate(email=email, password=password)

            if etudiant is None:
                messages.error(request, 'The student does not exist.')
            elif etudiant == 'incorrect_password':
                messages.error(request, 'The password is incorrect.')
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
            messages.error(request, "Please enter a valid email.")

        return redirect('login')  # Redirect back to login page

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
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Vérifier les mots de passe
        if password != confirm_password:
            return render(request, 'authentification/message.html', {'message': 'The passwords do not match'})

        # Vérifier si l'email existe déjà dans Professeur ou Etudiant
        if Professeur.objects.filter(email=email).exists() or Etudiant.objects.filter(email_etudiant=email).exists():
            return render(request, 'authentification/message.html', {'message': 'This email is already taken'})

        current_site = get_current_site(request)

        # Enregistrement des Professeurs
        if email.endswith('@enset-media.ac.ma'):
            professeur = Professeur(
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
            verification_link = f"http://{current_site.domain}/signup/?uid={uid}&token={token}"

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

        # Enregistrement des Étudiants
        elif email.endswith('-etu@etu.univh2c.ma'):
            etudiant = Etudiant(
                email_etudiant=email,
                password=make_password(password),
                nom=nom,
                prenom=prenom,
                last_login=None,
                is_verified=False
            )
            etudiant.save()

            uid = urlsafe_base64_encode(force_bytes(etudiant.pk))
            token = default_token_generator.make_token(etudiant)
            verification_link = f"http://{current_site.domain}/signup/?uid={uid}&token={token}"

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
            return render(request, 'authentification/message.html', {'message': 'Invalid email format.'})

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
    return redirect('login') 



