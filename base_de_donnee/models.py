from django.db import models
from django.contrib.auth.hashers import check_password
import uuid

# Manager personnalisé pour Professeur
class ProfesseurManager(models.Manager):
    def authenticate(self, email, password):
        try:
            professeur = self.get(EMAIL=email)  
            if check_password(password, professeur.PASSWORD):  
                return professeur
            else:
                return 'incorrect_password'
        except Professeur.DoesNotExist:
            return None

# Manager personnalisé pour Etudiant
class EtudiantManager(models.Manager):
    def authenticate(self, email, password):
        try:
            etudiant = self.get(EMAIL_ETUDIANT=email)  
            if check_password(password, etudiant.PASSWORD):  
                return etudiant
            else:
                return 'incorrect_password'
        except Etudiant.DoesNotExist:
            return None

from django.contrib.auth.models import AbstractUser

class Etudiant(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, null=True, blank=True)

    password = models.CharField(max_length=255)  # Store hashed passwords
    filiere = models.CharField(max_length=255)
    departement = models.CharField(max_length=255)
    projets = models.ManyToManyField('Project', related_name="etudiants")
    classes = models.ManyToManyField('Classe', related_name="etudiants")
    groupes = models.ManyToManyField('Groupe', related_name="membres")

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

    def set_password(self, raw_password):
        """Hashes and sets the password"""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Checks if the provided password is correct"""
        return check_password(raw_password, self.password)


class Professeur(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    departement = models.CharField(max_length=255)
    specialite = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

    def set_password(self, raw_password):
        """Hashes and sets the password"""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Checks if the provided password is correct"""
        return check_password(raw_password, self.password)

class Classe(models.Model):
    id = models.AutoField(primary_key=True)
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
    projet = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="groupes")
    
    def _str_(self):
        return self.nom_groupe

class Taches(models.Model):
    groupe = models.ForeignKey(Groupe, on_delete=models.CASCADE, related_name="taches")
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, related_name="taches")
    description_tache = models.TextField()
    status_choices = [
        ('En cours', 'En cours'),
        ('Terminé', 'Terminé'),
    ]
    status = models.CharField(max_length=25, choices=status_choices)
    deadline = models.DateField(null=False, blank=False)

    class Meta:
        verbose_name = "Tâche"
        verbose_name_plural = "Tâches"

    
    def _str_(self):
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