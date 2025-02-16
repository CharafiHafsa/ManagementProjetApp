from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Etudiant, Classe

@receiver(m2m_changed, sender=Etudiant.classes.through)
def update_student_count(sender, instance, action, **kwargs):
    """Update student count whenever a student is added/removed from a class."""
    if action in ["post_add", "post_remove", "post_clear"]:
        for classe in instance.classes.all():
            classe.etudiants_nbr = classe.etudiants.count()  # Get correct count
            classe.save(update_fields=['etudiants_nbr'])  # Save only the updated field
