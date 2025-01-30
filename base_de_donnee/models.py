from django.db import models
from django.contrib.auth.models import AbstractUser

# class Etudiant(models.Model):
#     filiere = models.CharField(max_length=255)
#     departement = models.CharField(max_length=255)
#     projets = models.ManyToManyField('Project', related_name="etudiants")
#     classes = models.ManyToManyField('Classe', related_name="etudiants")
#     groupes = models.ManyToManyField('Groupe', related_name="membres")
    
#     def __str__(self):
#         return f"{self.last_name} {self.first_name}"

# class Professeur(models.Model):
#     departement = models.CharField(max_length=255)
#     specialite = models.CharField(max_length=255)
    
#     def __str__(self):
#         return f"{self.last_name} {self.first_name}"

# class Classe(models.Model):
#     code_classe = models.CharField(max_length=255, primary_key=True)
#     nom_classe = models.CharField(max_length=255)
#     professeur = models.ForeignKey(Professeur, on_delete=models.CASCADE, related_name="classes")
    
#     def __str__(self):
#         return self.nom_classe

# class Project(models.Model):
#     description = models.TextField()
#     date_debut = models.DateField()
#     date_fin = models.DateField()
#     nom_project = models.CharField(max_length=255)
#     code_classe = models.ForeignKey(Classe, on_delete=models.CASCADE, related_name="projets")
    
#     def __str__(self):
#         return self.nom_project

# class Groupe(models.Model):
#     nom_groupe = models.CharField(max_length=255)
#     nbr_membre = models.PositiveIntegerField()
#     projet = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="groupes")
    
#     def __str__(self):
#         return self.nom_groupe

# class Taches(models.Model):
#     groupe = models.ForeignKey(Groupe, on_delete=models.CASCADE, related_name="taches")
#     etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, related_name="taches")
#     description_tache = models.TextField()
#     status_choices = [
#         ('En cours', 'En cours'),
#         ('Terminé', 'Terminé'),
#     ]
#     status = models.CharField(max_length=25, choices=status_choices)
#     deadline = models.DateField(null=False, blank=False)

#     class Meta:
#         verbose_name = "Tâche"
#         verbose_name_plural = "Tâches"

    
#     def __str__(self):
#         return f"{self.description_tache[:30]} - {self.status}"

# class Calendrier(models.Model):
#     couleurs = [
#         ('rouge', 'rouge'),
#         ('vert', 'vert'),
#         ('bleu', 'bleu'),
#         ('jaune', 'jaune'),
#     ]
#     etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, related_name="line_time")
#     evenement = models.CharField(max_length=255, null=True)
#     date_debut = models.DateField(null=True)
#     date_fin = models.DateField(null=True)
#     status = models.CharField(max_length=10, choices=couleurs)

class Etudiant(models.Model):
    IDETUDIANT = models.AutoField(primary_key=True)
    FILIERE = models.CharField(max_length=255, null=False)
    EMAIL_ETUDIANT = models.EmailField(null=False)
    PASSWORD = models.CharField(max_length=255, null=False)
    NOM = models.CharField(max_length=255, null=False)
    PRENOM = models.CharField(max_length=255, null=False)
    DEPARTEMENT = models.CharField(max_length=255, null=False)

    

class Professeur(models.Model):
    IDPROFESSEUR = models.AutoField(primary_key=True)
    DEPARTEMENT = models.CharField(max_length=255, null=False)
    SPECIALITE = models.CharField(max_length=255, null=False)
    EMAIL = models.EmailField(null=False)
    PASSWORD = models.CharField(max_length=255, null=False)
    NOM = models.CharField(max_length=255, null=False)
    PRENOM = models.CharField(max_length=255, null=False)

    

class Classe(models.Model):
    CODECLASSE = models.CharField(max_length=255, primary_key=True)
    NOM_CLASSE = models.CharField(max_length=255, null=False)

    

class Project(models.Model):
    IDPROJECT = models.AutoField(primary_key=True)
    CODECLASSE = models.ForeignKey(Classe, on_delete=models.CASCADE)
    DESCRIPTION = models.TextField(null=False)
    DATE_DEBUT = models.DateField(null=False)
    DATE_FIN = models.DateField(null=False)
    NOM_PROJECT = models.CharField(max_length=255, null=False)

   
class Groupe(models.Model):
    ID_GROUPE = models.AutoField(primary_key=True)
    IDPROJECT = models.ForeignKey(Project, on_delete=models.CASCADE)
    NOM_GROUPE = models.CharField(max_length=255, null=False)
    NBR_MEMBRE = models.IntegerField(null=False)

    def _str_(self):
        return self.NOM_GROUPE

class Avoir(models.Model):
    IDETUDIANT = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
    IDPROJECT = models.ForeignKey(Project, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('IDETUDIANT', 'IDPROJECT')

    

class Composer(models.Model):
    IDETUDIANT = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
    CODECLASSE = models.ForeignKey(Classe, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('IDETUDIANT', 'CODECLASSE')


class Construire(models.Model):
    IDETUDIANT = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
    ID_GROUPE = models.ForeignKey(Groupe, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('IDETUDIANT', 'ID_GROUPE')

    

class Creer(models.Model):
    IDPROFESSEUR = models.ForeignKey(Professeur, on_delete=models.CASCADE)
    CODECLASSE = models.ForeignKey(Classe, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('IDPROFESSEUR', 'CODECLASSE')

    

class Todoliste(models.Model):
    ID = models.AutoField(primary_key=True)
    IDETUDIANT = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
    DESCRIPTIONTACHE = models.TextField(null=False)
    STATUS = models.CharField(max_length=255, null=False)
    DEADLINE = models.DateField(null=False)