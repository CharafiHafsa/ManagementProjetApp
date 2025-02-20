from django.contrib import admin
from .models import Classe
from .models import Etudiant
from .models import Groupe
from .models import Professeur
from .models import Project
from .models import Taches
from .models import Calendrier
from .models import Event
from .models import Message
from .models import Document
from .models import Notification

admin.site.register(Classe)
admin.site.register(Etudiant)
admin.site.register(Groupe)
admin.site.register(Professeur)
admin.site.register(Project)
admin.site.register(Taches)
admin.site.register(Calendrier)
admin.site.register(Event)
admin.site.register(Message)
admin.site.register(Document)
admin.site.register(Notification)