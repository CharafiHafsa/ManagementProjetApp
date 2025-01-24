from django.db import models

# Create your models here.

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