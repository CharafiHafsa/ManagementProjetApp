from django.db import models
from django.contrib.auth.hashers import check_password
import uuid
from django.utils.timezone import now
import datetime
import random
from django.core.files import File
from django.conf import settings
import os
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError


# Manager personnalisé pour Professeur
class ProfesseurManager(models.Manager):
    def authenticate(self, email, password):
        try:
            professeur = self.get(email=email)  
            if check_password(password,professeur.password):  
                return professeur
            else:
                return 'incorrect_password'
        except Professeur.DoesNotExist:
            return None
# Manager personnalisé pour Etudiant
class EtudiantManager(models.Manager):
    def authenticate(self, email, password):
        try:
            etudiant = self.get(email_etudiant=email)  
            if check_password(password,etudiant.password):  
                return etudiant
            else:
                return 'incorrect_password'
        except Etudiant.DoesNotExist:
            return None

class Etudiant(models.Model):
    filiere = models.CharField(max_length=255, null=False)
    photo_profil = models.ImageField(upload_to='images/', default='images/profile.jpeg')
    departement = models.CharField(max_length=255, null=False)
    email_etudiant = models.EmailField(null=False)
    password = models.CharField(max_length=255, null=False)
    nom = models.CharField(max_length=255, null=False)
    prenom = models.CharField(max_length=255, null=False)
    last_login = models.DateTimeField(null=True, blank=True) 
    is_verified = models.BooleanField(default=False)
    objects = EtudiantManager()
    projets = models.ManyToManyField('Project', related_name="etudiants", blank=True)
    classes = models.ManyToManyField(
        'Classe',
        through='EtudiantClasse',
        related_name='etudiants',
        blank=True
    )
    groupes = models.ManyToManyField('Groupe', related_name="membres",  blank=True)
    groupesArchive = models.ManyToManyField('GroupeArchive', related_name="membres",  blank=True)
    
    def str(self):
        return f"{self.nom} {self.prenom}"
    def get_email_field_name(self):
        return 'email_etudiant'
    
class EtudiantClasse(models.Model):
    etudiant = models.ForeignKey('Etudiant', on_delete=models.CASCADE)
    classe = models.ForeignKey('Classe', on_delete=models.CASCADE)
    is_archived = models.BooleanField(default=False)

    class Meta:
        unique_together = ('etudiant', 'classe')  # empêche les doublons

    def __str__(self):
        return f"{self.etudiant.nom} - {self.classe.nom_classe} (Archivé: {self.is_archived})"

class Professeur(models.Model):
    departement = models.CharField(max_length=255, null=True)
    photo_profil = models.ImageField(upload_to='images/', default='images/profile.jpeg')
    specialite = models.CharField(max_length=255, null=True)
    email = models.EmailField(null=False,unique=True)
    password = models.CharField(max_length=255, null=False)
    nom = models.CharField(max_length=255, null=False)
    prenom = models.CharField(max_length=255, null=False)
    last_login = models.DateTimeField(null=True, blank=True)
    is_verified = models.BooleanField(default=False) 
    objects = ProfesseurManager()
    
    
    def str(self):
        return f"{self.nom} {self.prenom}"
    def get_email_field_name(self):
        return 'email'

class Classe(models.Model):
    code_classe = models.CharField(max_length=255, unique=True)
    nom_classe = models.CharField(max_length=255)
    professeur = models.ForeignKey(Professeur, on_delete=models.CASCADE, related_name="classes")
    description =models.CharField(default='nouveau classe')
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    is_archived = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.code_classe:
            self.code_classe = self.generate_unique_code()
        if not self.image:
            default_images = [
                'blog-img1.jpg',
                'blog-img2.jpg',
                'blog-img3.jpg',
                'blog-img4.jpg',
                'blog-img5.jpg'
            ]
            chosen = random.choice(default_images)
            image_path = os.path.join(settings.BASE_DIR, 'static','img','defaullt_classe_images', chosen)
            with open(image_path, 'rb') as f:
                self.image.save(chosen, File(f), save=False)
        super().save(*args, **kwargs)



    def generate_unique_code(self):
        return str(uuid.uuid4())[:8].upper()  # Generates an 8-character unique code

    def __str__(self):
        return f"{self.nom_classe} ({self.code_classe})"


    def _str_(self):
        return self.nom_classe

class Project(models.Model):
    description = models.TextField()
    date_debut = models.DateField()
    date_fin = models.DateField()
    nom_project = models.CharField(max_length=255)
    code_classe = models.ForeignKey(Classe, on_delete=models.CASCADE, related_name="projets")
    
    def __str__(self):
        return self.nom_project

    def save(self, *args, **kwargs):
        print(f"Saving project: {self.nom_project}")
        super().save(*args, **kwargs)

class Groupe(models.Model):
    nom_groupe = models.CharField(max_length=255)
    nbr_membre = models.PositiveIntegerField()
    projet = models.ForeignKey(
        Project, 
        on_delete=models.SET_NULL,  # Permet de garder le groupe même si le projet est supprimé
        null=True,   # Autorise NULL dans la base de données
        blank=True   # Autorise un formulaire vide en Django admin
    )
    meet_link = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def str(self):
        return self.nom_groupe

class GroupeArchive(models.Model):
    groupe = models.OneToOneField(
        Groupe,
        on_delete=models.CASCADE,
        related_name='archive',
        null=True,  # <-- Ajoute ceci
        blank=True  # <-- Optionnel si tu veux permettre un champ vide dans les formulaires
    )
    nom_groupe = models.CharField(max_length=255)
    nbr_membre = models.PositiveIntegerField()
    projet = models.ForeignKey(
        Project, 
        on_delete=models.SET_NULL,  # Permet de garder le groupe même si le projet est supprimé
        null=True,   # Autorise NULL dans la base de données
        blank=True   # Autorise un formulaire vide en Django admin
    )

    def str(self):
        return self.nom_groupe

class Taches(models.Model):
    groupe = models.ForeignKey(Groupe, on_delete=models.CASCADE, related_name="taches", null=True, blank=True)
    groupeArchive = models.ForeignKey(GroupeArchive, on_delete=models.CASCADE, related_name="taches_archive", null=True, blank=True)
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, related_name="taches")
    description_tache = models.TextField()
    status_choices = [
        ('En cours', 'En cours'),
        ('Terminé', 'Terminé'),
    ]
    status = models.CharField(max_length=25, choices=status_choices, default='En cours')
    deadline = models.DateField(null=False, blank=False)

    class Meta:
        verbose_name = "Tâche"
        verbose_name_plural = "Tâches"

    
    def str(self):
        return f"{self.description_tache[:30]} - {self.status}"

class Calendrier(models.Model):
    couleurs = [
        ('rouge', 'rouge'),
        ('vert', 'vert'),
        ('bleu', 'bleu'),
        ('jaune', 'jaune'),
    ]
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, related_name="line_time")
    evenement = models.CharField(max_length=255, null=True)
    date_debut = models.DateField(null=True)
    date_fin = models.DateField(null=True)
    status = models.CharField(max_length=10, choices=couleurs)

class Event(models.Model):
    title = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    category = models.CharField(max_length=50)  # Correspond à "calendar" dans tes données
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, related_name="events", null=True, blank=True)

    def clean(self):
        if self.end_date and self.start_date and self.end_date <= self.start_date:
            raise ValidationError({'end_date': "La date de fin doit être postérieure à la date de début."})

    def __str__(self):
        return self.title

class Message(models.Model):
    groupe = models.ForeignKey(Groupe, on_delete=models.CASCADE, related_name="messages")
    groupeArchive = models.ForeignKey(GroupeArchive, on_delete=models.CASCADE, related_name="messages", null=True, blank=True) 
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, related_name="messages")
    contenu = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)

class Document(models.Model):
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    groupe = models.ForeignKey(Groupe,on_delete=models.CASCADE, related_name='documents', null=True, blank=True)
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, related_name='documents')
    groupeArchive = models.ForeignKey(GroupeArchive, on_delete=models.CASCADE, related_name='documents_archive', null=True, blank=True)

class Notification(models.Model):
    etudiant = models.ForeignKey(Etudiant,  on_delete=models.CASCADE, related_name='notifications' )
    groupe = models.ForeignKey( Groupe,  on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    groupeArchive = models.ForeignKey(GroupeArchive, on_delete=models.CASCADE, related_name='notifications_archive', null=True, blank=True)

class HistoriqueTachesEtu(models.Model):
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, related_name="historique_taches")
    date = models.DateField(default=timezone.now)  # Un enregistrement par jour
    taches_en_cours = models.IntegerField(default=0)
    taches_terminees = models.IntegerField(default=0)
    taches_en_retard = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Historique des Tâches"
        verbose_name_plural = "Historiques des Tâches"
        ordering = ['-date']  # Trie par date décroissante

class P_ressources(models.Model):
    titre = models.CharField(max_length=255)
    file = models.FileField(upload_to='resources/', null=True, blank=True)
    video_url = models.URLField(null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    date_ajout = models.DateTimeField(auto_now_add=True)
    projet = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='ressources')  

    def __str__(self):
        return f"Ressource: {self.titre} ({self.projet.nom_project})"
  
class TempsUtilisation(models.Model):
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, related_name="historique_temps")
    date = models.DateField(default=timezone.now)  # Un enregistrement par jour
    date_start_counter = models.DateTimeField(null=True, blank=True)
    temps_passe = models.DurationField(default=timedelta(seconds=0))  # Stocke le temps en hh:mm:ss

    class Meta:
        verbose_name = "Historique du Temps d'Utilisation"
        verbose_name_plural = "Historiques du Temps d'Utilisation"
        ordering = ['-date']  # Trie par date décroissante

class Sujet(models.Model):
    titre = models.CharField(max_length=255)
    groupe = models.ForeignKey(Groupe, on_delete=models.CASCADE)
    GroupeArchive = models.ForeignKey(GroupeArchive, on_delete=models.CASCADE, null=True, blank=True) 

    def _str_(self):
        return self.titre

class ChatMessage(models.Model):
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE,null=True, blank=True)
    sujet = models.ForeignKey(Sujet, on_delete=models.CASCADE)
    contenu = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return self.contenu[:20]

class Announce(models.Model):
    projet = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="annonces")
    contenu = models.TextField()
    date_publication = models.DateTimeField(default=now)

    def str(self):
        return f"Annonce for {self.projet.nom_project} - {self.date_publication.strftime('%Y-%m-%d %H:%M')}"

class Instruction(models.Model):
    projet = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="instructions")
    titre = models.CharField(max_length=255)  # Title of the instruction
    date_limite = models.DateField(null=True, blank=True)  # Optional deadline
    livrable_requis = models.BooleanField(default=False)  # If a deliverable is required

    def str(self):
        return f"Instruction: {self.titre} ({self.projet.nom_project})"

class InstructionStatus(models.Model):
    instruction = models.ForeignKey(Instruction, on_delete=models.CASCADE, related_name="statuses")
    groupe = models.ForeignKey(Groupe, on_delete=models.CASCADE, related_name="instructions_status")
    est_termine = models.BooleanField(default=False)  # Whether the group marked it as done
    fichier_livrable = models.FileField(upload_to='livrables/', null=True, blank=True)  # Optional file upload

    def str(self):
        return f"{self.groupe.nom_groupe} - {self.instruction.titre} ({'Done' if self.est_termine else 'Pending'})"

class P_ressources(models.Model):
    titre = models.CharField(max_length=255)
    file = models.FileField(upload_to='resources/', null=True, blank=True)
    video_url = models.URLField(null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    date_ajout = models.DateTimeField(auto_now_add=True)
    projet = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='ressources')  

    def str(self):
        return f"Ressource: {self.titre} ({self.projet.nom_project})"

class PENotification(models.Model):
    etudiants = models.ManyToManyField('Etudiant', related_name="pnotifications", blank=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    def _str_(self):
        return self.title

class ProfNotification(models.Model):
    professeur = models.ForeignKey(Professeur, on_delete=models.CASCADE, related_name="pnotifications")
    title = models.CharField(max_length=255)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.professeur.nom} - {self.title}"

class PEvent(models.Model):
    title = models.CharField(max_length=200)
    start = models.DateField(default=datetime.date.today)
    end = models.DateField()
    color = models.CharField(max_length=50)  # Default FullCalendar color
    professeur = models.ForeignKey(Professeur, on_delete=models.CASCADE, default=1)  # Add this line

    def __str__(self):
        return self.title
