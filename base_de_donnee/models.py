from django.db import models
from django.contrib.auth.hashers import check_password
import uuid
from django.utils.timezone import now
import datetime


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
    classes = models.ManyToManyField('Classe', related_name="etudiants",  blank=True)
    groupes = models.ManyToManyField('Groupe', related_name="membres",  blank=True)
    
    def str(self):
        return f"{self.nom} {self.prenom}"
    def get_email_field_name(self):
        return 'email_etudiant'

class Professeur(models.Model):
    departement = models.CharField(max_length=255, null=False)
    photo_profil = models.ImageField(upload_to='images/', default='images/profile.jpeg')
    specialite = models.CharField(max_length=255, null=False)
    email = models.EmailField(null=False)
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


    def save(self, *args, **kwargs):
        if not self.code_classe:
            self.code_classe = self.generate_unique_code()
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
    
    def _str_(self):
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

    def str(self):
        return self.nom_groupe

class Instruction(models.Model):
    projet = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="instructions")
    titre = models.CharField(max_length=255)  # Title of the instruction
    date_limite = models.DateField(null=True, blank=True)  # Optional deadline
    livrable_requis = models.BooleanField(default=False)  # If a deliverable is required

    def __str__(self):
        return f"Instruction: {self.titre} ({self.projet.nom_project})"

class InstructionStatus(models.Model):
    instruction = models.ForeignKey(Instruction, on_delete=models.CASCADE, related_name="statuses")
    groupe = models.ForeignKey(Groupe, on_delete=models.CASCADE, related_name="instructions_status")
    est_termine = models.BooleanField(default=False)  # Whether the group marked it as done
    fichier_livrable = models.FileField(upload_to='livrables/', null=True, blank=True)  # Optional file upload

    def __str__(self):
        return f"{self.groupe.nom_groupe} - {self.instruction.titre} ({'Done' if self.est_termine else 'Pending'})"

class Announce(models.Model):
    projet = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="annonces")
    contenu = models.TextField()
    date_publication = models.DateTimeField(default=now)

    def __str__(self):
        return f"Annonce for {self.projet.nom_project} - {self.date_publication.strftime('%Y-%m-%d %H:%M')}"

class P_ressources(models.Model):
    titre = models.CharField(max_length=255)
    file = models.FileField(upload_to='resources/', null=True, blank=True)
    video_url = models.URLField(null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    date_ajout = models.DateTimeField(auto_now_add=True)
    projet = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='ressources')  

    def __str__(self):
        return f"Ressource: {self.titre} ({self.projet.nom_project})"
  


class Taches(models.Model):
    groupe = models.ForeignKey(Groupe, on_delete=models.CASCADE, related_name="taches")
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
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, related_name="messages")
    contenu = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)

class Document(models.Model):
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    groupe = models.ForeignKey(Groupe,on_delete=models.CASCADE, related_name='documents')

class Notification(models.Model):
    etudiant = models.ForeignKey(Etudiant,  on_delete=models.CASCADE, related_name='notifications' )
    groupe = models.ForeignKey( Groupe,  on_delete=models.CASCADE, related_name='notifications')