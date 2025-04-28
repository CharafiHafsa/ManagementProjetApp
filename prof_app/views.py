from django.shortcuts import render , redirect , get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from base_de_donnee.models import *
from base_de_donnee.models import *
from django.core.files.storage import FileSystemStorage
import requests
import google.generativeai as genai
import markdown
from django.utils.timezone import now
from django.db.models import Count
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt


genai.configure(api_key="AIzaSyBNRe5yW4uRQNmjg1GcEZEpiXuPysY7xrQ")

def prof_accueil(request):
    prof_id = request.session.get('user_id')
    prof = Professeur.objects.filter(id=prof_id).first()
    
    # Filter only the professor's classes
    recent_classes = Classe.objects.filter(professeur=prof).order_by('-id')[:5]

    # Get projects only from the professor's classes
    recent_projects = Project.objects.filter(code_classe__professeur=prof).order_by('-id')[:5]

    # Get instructions from the professor’s projects
    upcoming_instructions = Instruction.objects.filter(
        projet__code_classe__professeur=prof,
        date_limite__gte=now()
    ).order_by('date_limite')[:5]

    # Announcements from the professor’s projects
    recent_announces = Announce.objects.filter(
        projet__code_classe__professeur=prof
    ).order_by('-date_publication')[:5]

    class_stats = []
    for classe in recent_classes:
        num_projects = classe.projets.count()
        num_students = classe.etudiants.count()
        class_stats.append({
            'classe': classe,
            'num_projects': num_projects,
            'num_students': num_students
        })

    
    # Only groups from the professor’s projects
    groupes = Groupe.objects.filter(projet__code_classe__professeur=prof)
    for g in groupes:
        total = g.instructions_status.count()
        done = g.instructions_status.filter(est_termine=True).count()
        g.progression = int((done / total) * 100) if total > 0 else 0

    context = {
        'professeur': prof,
        'recent_classes': recent_classes,
        'recent_projects': recent_projects,
        'upcoming_instructions': upcoming_instructions,
        'recent_announces': recent_announces,
        'groupes': groupes,
        'class_stats': class_stats  # Adding the class statistics to the context
    }
    return render(request, 'prof/home.html', context)
    
    

def get_class_stats(request, class_id):
    try:
        classe = Classe.objects.get(id=class_id)
        # Assuming you want to return students and projects stats
        students_count = classe.etudiants.count()  # Modify as per your model
        projects_count = classe.projets.count()  # Modify as per your model
        
        return JsonResponse({
            'students': students_count,
            'projects': projects_count,
        })
    except Classe.DoesNotExist:
        return JsonResponse({'error': 'Class not found'}, status=404)

def prof_classes(request):
    prof_id = request.session.get('user_id')
    if not prof_id:
        return redirect('login')  # Redirect to login if user_id is missing

    # Get the professor with the ID from the session
    prof = Professeur.objects.filter(id=prof_id).first()

    # Get the search query if provided
    query = request.GET.get('q', '')

    if prof:
        # Filter the classes assigned to the professor
        classes = Classe.objects.filter(professeur=prof)

        # If there's a search query, filter the classes by name
        if query:
            classes = classes.filter(nom_classe__icontains=query)  # Filter by class name

        # Calculate the student count for each class
        for classe in classes:
            classe.etudiants_count = classe.etudiants.count()
            classe.projects_count = classe.projets.count()
    else:
        print("No professor found.")  # Debugging line
        classes = []  # If no professor is found, return an empty list

    return render(request, 'prof/classes.html', {'professor': prof, 'classes': classes, 'query': query})

def create_class(request):
    if request.method == 'POST' :
        className = request.POST.get('className')
        prof_id = request.session.get('user_id')
        prof = Professeur.objects.filter(id=prof_id).first()

        if not className :
            messages.error(request, "Nom requeired", extra_tags="classes")

        elif not prof:
            messages.error(request, "Professeur introuvalble", extra_tags="classes")
        else:
            new_Classe = Classe(nom_classe=className, professeur = prof)

            new_Classe.save()
            messages.success(request, f"Classe {className} added with code {new_Classe.code_classe }!", extra_tags="classes")

            return redirect('prof_classes')
    return render(request, 'prof/classes.html')

def edit_classe(request, class_id):

    classe = get_object_or_404(Classe, id=class_id)
    
    if request.method == "POST":
        class_name = request.POST.get("className")
        class_desc = request.POST.get("classdesc")

        if class_name or class_desc:
            classe.nom_classe = class_name
            classe.description = class_desc
            classe.save()
            messages.success(request, "Class updated successfully!", extra_tags="classes")
        else:
            messages.error(request, "Please fill all fields.", extra_tags="classes")

    next_url = request.GET.get("next", "prof_classes")
    return redirect(next_url)  # Redirect to the main page

def delete_classe(request, class_id):
    classe = get_object_or_404(Classe, id=class_id)

    if request.method == 'POST':
        classe.delete()
        messages.success(request, "class and all related data is deleted successfully!", extra_tags="classes")
        return redirect("prof_classes")

    return redirect("prof_classes")

def classe_detail(request, class_id):
    classe = get_object_or_404(Classe, id=class_id)
    prof_id = request.session.get('user_id')
    professor = Professeur.objects.filter(id=prof_id).first()
    projects = Project.objects.filter(code_classe=classe)

    # Ajoute les étudiants et projets
    etudiants = classe.etudiants.all()
    projets = classe.projets.all()

    etudiants_data = []
    for etudiant in etudiants:
        projets_participation = []
        for projet in projets:
            groupe = projet.groupe_set.filter(membres=etudiant).first()
            projets_participation.append({
                'nom_projet': projet.nom_project,
                'groupe': groupe.nom_groupe if groupe else None
            })
        etudiants_data.append({
            'etudiant': etudiant,
            'projets': projets_participation
        })

    return render(request, 'prof/classe.html', {
        'professor': professor,
        'classe': classe,
        'projects': projects,
        'etudiants_data': etudiants_data,  # ← essentiel pour afficher la liste
    })


def supprimer_etudiant(request, etudiant_id):
    etudiant = get_object_or_404(Etudiant, id=etudiant_id)
    classe_id = etudiant.classes.first().id if etudiant.classes.exists() else None

    if request.method == 'POST':
        etudiant.delete()
        return redirect('classe_detail', class_id=classe_id)

    return redirect('classe_detail', class_id=classe_id)

def add_project(request, class_id):
    classe = Classe.objects.get(id=class_id)
    prof_id = request.session.get('user_id')
    if not prof_id:
        messages.error(request, "Votre session a expire")
        return redirect('login')
    professor = Professeur.objects.filter(id=prof_id).first()

    if request.method == 'POST':
        nom_project = request.POST.get("nom_project")
        description = request.POST.get("description")
        date_debut = request.POST.get("date_debut")
        date_fin = request.POST.get("date_fin")

        print(f"Received data: {nom_project}, {description}, {date_debut}, {date_fin}")

        if nom_project and description and date_debut and date_fin:
            try:
                new_project = Project(
                    nom_project=nom_project,
                    description=description,
                    date_debut=date_debut,
                    date_fin=date_fin,
                    code_classe=classe
                )
                new_project.save()
                print(f"Saved project: {new_project.nom_project}")
                messages.success(request, "Projet ajouté avec succès !", extra_tags="projet")
                PNotification.objects.create(
                    title="Nouveau projet ajouté",
                    content=f"Le projet '{nom_project}' a été ajouté à votre classe.",
                    destination_type='class',
                    classe=classe
                )
                
            except Exception as e:
                print(f"Error: {e}")
                messages.error(request, f"Erreur lors de l'ajout du projet: {e}", extra_tags="projet")

            return redirect('classe_detail', class_id=classe.id)

    return render(request, 'prof/classe.html', {'classe': classe, 'professor': professor})

def edit_projet(request, projet_id):
    projet = get_object_or_404(Project, id=projet_id)

    if request.method == "POST":
        nom_project = request.POST.get('projetName')
        description = request.POST.get('projetdesc')
        date_debut = request.POST.get('date_debut')
        date_fin = request.POST.get('date_fin')

        # Update only the fields that are not empty
        updated = False
        if nom_project:
            projet.nom_project = nom_project
            updated = True
        if description:
            projet.description = description
            updated = True
        if date_debut:
            projet.date_debut = date_debut
            updated = True
        if date_fin:
            projet.date_fin = date_fin
            updated = True

        if updated:
            projet.save()
            messages.success(request, "Project updated successfully!", extra_tags="projet")
        else:
            messages.error(request, "Please fill all fields.", extra_tags="projet")

    next_url = request.GET.get("next", "projet_detail")
    return redirect(next_url)

def delete_projet(request, projet_id):
    projet =get_object_or_404(Project, id = projet_id)

    if request.method == "POST" :
        projet.delete()
        messages.success(request, "projet and all related data is deleted successfully!",extra_tags="projet")


        return redirect('classe_detail', class_id = projet.code_classe_id)

    return redirect('classe_detail', class_id = projet.code_classe_id)

def projet_detail(request, projet_id):
    
    prof_id = request.session.get('user_id')
    prof = Professeur.objects.filter(id=prof_id).first()
    projet = get_object_or_404(Project, id=projet_id)
    
    instructions = projet.instructions.all()
    total_groups_count = Groupe.objects.filter(projet=projet).count()
    total_students_count = sum(groupe.nbr_membre for groupe in Groupe.objects.filter(projet=projet))
    
    announces = Announce.objects.filter(projet=projet).order_by("-date_publication")
    ressources = P_ressources.objects.filter(projet=projet).order_by("-date_ajout")
    groupes = Groupe.objects.filter(projet=projet)
    instruction_stats = []
    completed_instructions = 0
    
    for instruction in instructions:
        completed_groups_count = InstructionStatus.objects.filter(instruction=instruction, est_termine=True).count()
        pending_groups_count = total_groups_count - completed_groups_count
        
        instruction_stats.append({
            'instruction': instruction,
            'completed_groups': completed_groups_count,
            'pending_groups': pending_groups_count,
            'total_groups': total_groups_count,
            'deadline': instruction.date_limite
        })
        
        if completed_groups_count == total_groups_count and total_groups_count > 0:
            completed_instructions += 1
    
    total_instructions = len(instruction_stats)
    pending_instructions = total_instructions - completed_instructions
    completion_percentage = (completed_instructions / total_instructions) * 100 if total_instructions else 0
    
    return render(request, 'prof/projet.html', {
        'professeur': prof,
        'projet': projet,
        'total_groups': total_groups_count,
        'total_students': total_students_count,
        'total_instructions': total_instructions,
        'instruction_stats': instruction_stats,
        'completed_instructions': completed_instructions,
        'pending_instructions': pending_instructions,
        'completion_percentage': completion_percentage,
        'announces': announces,
        'ressources': ressources,
        'groupes' : groupes,
    })



def add_instruction(request, projet_id):
    if request.method == "POST":
        titre = request.POST.get("titre")
        date_limite = request.POST.get("date_limite")
        livrable_requis = request.POST.get("livrable_requis") == "on"

        projet = get_object_or_404(Project, id=projet_id)
        instruction = Instruction.objects.create(
            projet=projet,
            titre=titre,
            date_limite=date_limite if date_limite else None,
            livrable_requis=livrable_requis
        )

        for groupe in projet.groupe_set.all():
            PNotification.objects.create(
                title="Nouvelle instruction",
                content=f"Une nouvelle instruction a été ajoutée pour le projet '{projet.nom_project}'.",
                destination_type='group',
                groupe=groupe
        )

        return redirect('projet_detail', projet_id=projet.id)

    return JsonResponse({"error": "Invalid request"}, status=400)


def edit_instruction(request, id):
    instruction = get_object_or_404(Instruction, id=id)
    
    if request.method == 'POST':
        titre = request.POST.get('titre')
        date_limite = request.POST.get('date_limite') or None
        livrable_requis = 'livrable_requis' in request.POST

        instruction.titre = titre
        instruction.date_limite = date_limite
        instruction.livrable_requis = livrable_requis
        instruction.save()
        
        messages.success(request, "L'instruction a été modifiée avec succès.")
        return redirect('projet_detail', projet_id=instruction.projet.id)  # replace with your actual view name

        return redirect("projet_detail", projet_id= projet.id)
 # fallback

# Delete instruction
def delete_instruction(request, id):
    instruction = get_object_or_404(Instruction, id=id)
    projet_id = instruction.projet.id  # save this before deleting
    instruction.delete()
    messages.success(request, "L'instruction a été supprimée avec succès.")
    return redirect('projet_detail', projet_id=projet_id)


def add_announce(request, projet_id):
    if request.method == 'POST':
        projet = get_object_or_404(Project, id=projet_id)
        contenu = request.POST.get("contenu")

        if contenu:
            Announce.objects.create(projet=projet, contenu=contenu)
            messages.success(request, "Annonce ajoutée avec succès.", extra_tags="projet")

            # 🔔 Notifier tous les groupes associés au projet
            for groupe in projet.groupe_set.all():
                PNotification.objects.create(
                    title="Nouvelle annonce",
                    content=f"Une annonce a été publiée pour le projet '{projet.nom_project}'.",
                    destination_type='group',
                    groupe=groupe
                )
        else:
            messages.error(request, "Le contenu ne peut pas être vide.", extra_tags="projet")

    return redirect("projet_detail", projet_id=projet_id)

def delete_announce(request, announce_id):
    announce = get_object_or_404(Announce, id=announce_id)
    projet_id = announce.projet.id
    announce.delete()
    messages.success(request, "Announce supprimee ave succes ",extra_tags="projet")
    return redirect("projet_detail", projet_id=projet_id)

def modify_announce(request, announce_id):
    announce = get_object_or_404(Announce, id=announce_id)

    if request.method == 'POST':
        nouveau_contentu = request.POST.get("contenu")
        if nouveau_contentu :
            announce.contenu = nouveau_contentu
            announce.save()
            messages.success(request, "Announce modifee avec succes",extra_tags="projet")
        else:
            messages.error(request, "Le contenu ne peut pas etre vide",extra_tags="projet")
    return redirect("projet_detail", projet_id=announce.projet.id)

def add_ressource(request, projet_id):
    projet = get_object_or_404(Project, id=projet_id)

    if request.method == 'POST':
        titre = request.POST.get("titre")
        video_url = request.POST.get("video_url", "").strip()
        file = request.FILES.get("file")
        url = request.POST.get("url", "").strip()

        if not titre:
            messages.error(request, "Le titre est requis.", extra_tags="projet")
            return redirect("projet_detail", projet_id=projet.id)

        if not file and not video_url and not url:
            messages.error(request, "Vous devez ajouter une ressource (fichier, URL ou vidéo).", extra_tags="projet")
            return redirect("projet_detail", projet_id=projet.id)

        # ✅ Créer la ressource
        ressource = P_ressources.objects.create(
            projet=projet,
            titre=titre,
            file=file if file else None,
            video_url=video_url if video_url else None,
            url=url if url else None
        )

        messages.success(request, "Ressource ajoutée avec succès.", extra_tags="projet")

        # 🔔 Notifier tous les groupes associés au projet
        for groupe in projet.groupe_set.all():
            PNotification.objects.create(
                title="Nouvelle ressource",
                content=f"Une nouvelle ressource a été ajoutée pour le projet '{projet.nom_project}'.",
                destination_type='group',
                groupe=groupe
            )

    return redirect("projet_detail", projet_id=projet.id)

def delete_ressource(request, ressource_id):
    ressource = get_object_or_404(P_ressources, id=ressource_id)
    projet_id = ressource.projet.id
    ressource.delete()
    messages.success(request, "Ressource supprimée avec succès",extra_tags="projet")
    return redirect("projet_detail", projet_id=projet_id)

def groupe_stats_view(request, projet_id, groupe_id):
    groupe = get_object_or_404(Groupe, id=groupe_id, projet__id=projet_id)
    instructions_status = InstructionStatus.objects.filter(groupe=groupe).select_related('instruction')
    prof_id = request.session.get('user_id')
    prof = Professeur.objects.filter(id=prof_id).first()
    projet = get_object_or_404(Project, id=projet_id)

    taches_du_groupe = Taches.objects.filter(groupe=groupe).select_related('etudiant')

    instructions_data = []
    today = now().date()

    # STATS INIT
    total_instructions = instructions_status.count()
    completed_instructions = instructions_status.filter(est_termine=True).count()
    incompleted_instructions = total_instructions - completed_instructions

    total_tasks = taches_du_groupe.count()
    completed_tasks = taches_du_groupe.filter(status='Terminé').count()
    incompleted_tasks = total_tasks - completed_tasks

    total_students = groupe.membres.count()

    for status in instructions_status:
        instruction = status.instruction
        en_retard = instruction.date_limite and not status.est_termine and today > instruction.date_limite

        instructions_data.append({
            'titre': instruction.titre,
            'est_termine': status.est_termine,
            'date_limite': instruction.date_limite,
            'livrable_requis': instruction.livrable_requis,
            'fichier_livrable': status.fichier_livrable.url if status.fichier_livrable else None,
            'en_retard': en_retard
        })

    membres = groupe.membres.all()
    membres_data = []

    for membre in membres:
        taches = membre.taches.filter(groupe=groupe)
        nb_total = taches.count()
        nb_terminees = taches.filter(status='Terminé').count()

        membres_data.append({
            'id': membre.id,
            'nom': membre.nom,
            'prenom': membre.prenom,
            'email_etudiant': membre.email_etudiant,
            'photo_profil': membre.photo_profil,
            'filiere': membre.filiere,
            'departement': membre.departement,
            'last_login': membre.last_login,
            'is_verified': membre.is_verified,
            'nb_taches_total': nb_total,
            'nb_taches_terminees': nb_terminees,
            'taches': taches
        })

    return render(request, 'prof/groupe.html', {
        'groupe': groupe,
        'professeur': prof,
        'projet': projet,
        'instructions': instructions_data,
        'membres': membres_data,
        'taches': taches_du_groupe,

        # 🔽 STATS TO DISPLAY IN TEMPLATE
        'total_instructions': total_instructions,
        'completed_instructions': completed_instructions,
        'incompleted_instructions': incompleted_instructions,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'incompleted_tasks': incompleted_tasks,
        'total_students': total_students,
        'today': now().date(),
    })


def notifier_champ_manquant(request, projet_id, groupe_id, etudiant_id, champ):
    if request.method == 'POST':
        etudiant = get_object_or_404(Etudiant, id=etudiant_id)
        projet = get_object_or_404(Project, id=projet_id)
        groupe = get_object_or_404(Groupe, id=groupe_id)
        

        champs_traduction = {
            'filiere': "Veuillez renseigner votre filière.",
            'departement': "Veuillez renseigner votre département.",
            'last_login': "Veuillez vous connecter au moins une fois.",
        }

        message = champs_traduction.get(champ, "Veuillez compléter vos informations personnelles.")

        # Création de la notification
        PNotification.objects.create(
            title="Information manquante",
            content=f"{message} (Projet: {projet.nom_project})",
            destination_type='student',
            student=etudiant
        )

        messages.success(request, f"Notification envoyée à {etudiant.nom} {etudiant.prenom}.", extra_tags="groupe")
        
        return redirect(request.META.get('HTTP_REFERER', '/'))


def chat_view(request):
    if request.method == 'POST':
        user_message = request.POST.get('message', '')

        # Gestion des questions sur la date
        if "date" in user_message or "today" in user_message:
            today_date = datetime.datetime.today().strftime("%A, %d %B %Y")
            return JsonResponse({'response': f"Today's date is {today_date}."})

        model = genai.GenerativeModel("gemini-2.0-flash")
        chat = model.start_chat()

        # Demander des réponses plus courtes
        response = chat.send_message(
            f"{user_message} (Réponds courts de manière claire et précise.)",
            generation_config={
                "max_output_tokens": 300,    # Limite la taille de la réponse
                "temperature": 0.7,         # Contrôle la créativité (0 = précis, 1 = aléatoire)
                "top_p": 0.9,               # Fait varier légèrement les réponses
                "top_k": 40                 # Sélectionne les meilleurs tokens pour plus de diversité
            }
        )

        formatted_response = markdown.markdown(response.text) 
        return JsonResponse({'response': formatted_response})

    return render(request, 'prof/chat.html')

def update_instruction_status(request, project_id, groupe_id):
    project = get_object_or_404(Project, id=project_id)
    group = get_object_or_404(Groupe, id=groupe_id, projet=project)
    instructions = Instruction.objects.filter(projet=project)

    instruction_statuses = [
        {'instruction': instruction, 'status': InstructionStatus.objects.filter(groupe=group, instruction=instruction).first()}
        for instruction in instructions
    ]

    if request.method == 'POST':
        instruction_id = request.POST.get("instruction_id")
        status = request.POST.get("status") == "on"
        instruction = get_object_or_404(Instruction, id=instruction_id)

        instruction_status, created = InstructionStatus.objects.get_or_create(
            instruction=instruction,
            groupe=group,
            defaults={'est_termine': status}
        )

        if not created:
            instruction_status.est_termine = status

        if 'upload_file' in request.FILES:
            file = request.FILES['upload_file']
            fs = FileSystemStorage()
            filename = fs.save(file.name, file)
            instruction_status.fichier_livrable = filename

        instruction_status.save()

        return redirect('update_instruction_status', project_id=project.id, groupe_id=group.id)

    return render(request, 'prof/student_instructions.html', {
        'project': project,
        'group': group,
        'instruction_statuses': instruction_statuses,
        'instructions': instructions
    })


def prof_notification(request):
    return render(request, 'prof/notification.html')

def prof_profile(request):
    return render(request, 'prof/profile.html')


def prof_settings(request):
    return render(request, 'prof/settings.html')


def prof_calender(request):
    return render(request, 'prof/calender.html')

def project_list(request):
    search_query = request.GET.get('search', '')
    class_filter = request.GET.get('class_filter', '')

    projets = Project.objects.all()
    
    if search_query:
        projets = projets.filter(nom_project__icontains=search_query)
    if class_filter:
        projets = projets.filter(code_classe__id=class_filter)

    classes = Classe.objects.all()
    today = timezone.now().date()

    context = {
        'projets': projets,
        'classes': classes,
        'today': today,
    }
    return render(request, 'prof/projets.html', context)



def calendar_view(request):
    projects = Project.objects.all()
    events = PEvent.objects.all()

    all_events = []

    for projet in projects:
        all_events.append({
            'title': f"Deadline: {projet.nom_project}",
            'start': str(projet.date_fin),
            'color': 'red'
        })

    for event in events:
        all_events.append({
            'title': event.title,
            'start': str(event.date),
            'color': 'blue'
        })

    context = {
        'events': json.dumps(all_events)
    }
    return render(request, 'prof/calendar.html', context)

@csrf_exempt
def add_event(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        title = data.get('title')
        date = data.get('date')
        Event.objects.create(title=title, date=date)
        return JsonResponse({'message': 'Événement ajouté avec succès !'})
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
