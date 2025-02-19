from django.shortcuts import render , redirect , get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from base_de_donnee.models import Professeur
from base_de_donnee.models import Classe , Etudiant , Project , Groupe, InstructionStatus, Instruction
from django.core.files.storage import FileSystemStorage


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




def prof_accueil(request):
    # Hardcoded email for testing
    test_email = 'hafsa.charafi@enset-media.ac.ma'
    
    # Get the professor's information based on the hardcoded email
    professor = get_object_or_404(Professeur, email=test_email)
    
    # Fetch the classes for the professor
    classes = Classe.objects.filter(professeur=professor)
    
    # Calculate global statistics
    total_classes = classes.count()
    total_students = Etudiant.objects.filter(classes__in=classes).count()  # Use 'classes' here
    total_projects = Project.objects.filter(code_classe__in=classes).count()  # Use 'code_classe' here
    
    # Pass the necessary data to the template
    context = {
        'professor': professor,
        'classes': classes,
        'total_classes': total_classes,
        'total_students': total_students,
        'total_projects': total_projects
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
    prof = Professeur.objects.filter(email="hafsa.charafi@enset-media.ac.ma").first()  # Get the professor with the email
    query = request.GET.get('q', '')

    if prof:
        classes = Classe.objects.filter(professeur=prof)  
        for classe in classes:
            classe.etudiants_count = classe.etudiants.count()
    else:
        print("No professor found.")  # Debugging line
        classes = []  # If no professor is found, return an empty list
    if query:
        classes = Classe.objects.filter(nom_classe__icontains=query)  # Filter by class name
    else:
        classes = Classe.objects.all()  # If no search, return all classes
    return render(request, 'prof/classes.html', {'professor': prof, 'classes': classes , 'query' : query})

def create_class(request):
    if request.method == 'POST' :
        className = request.POST.get('className')
        test_email = 'hafsa.charafi@enset-media.ac.ma'
        prof = Professeur.objects.filter(email=test_email).first()

        if not className :
            messages.error(request, "Nom requeired")

        elif not prof:
            messages.error(request, "Professeur introuvalble")
        else:
            new_Classe = Classe(nom_classe=className, professeur = prof)

            new_Classe.save()
            messages.success(request, f"Classe {className} added with code {new_Classe.code_classe }!")

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
            messages.success(request, "Class updated successfully!")
        else:
            messages.error(request, "Please fill all fields.")

    next_url = request.GET.get("next", "prof_classes")
    return redirect(next_url)  # Redirect to the main page

def delete_classe(request, class_id):
    classe = get_object_or_404(Classe, id=class_id)

    if request.method == 'POST':
        classe.delete()
        messages.success(request, "class and all related data is deleted successfully!")
        return redirect("prof_classes")

    return redirect("prof_classes")

def classe_detail(request, class_id):
    classe = get_object_or_404(Classe, id=class_id)
    test_email = 'hafsa.charafi@enset-media.ac.ma'
    prof = Professeur.objects.filter(email=test_email).first()
    professor = Professeur.objects.filter(email=test_email).first()
    projects = Project.objects.filter(code_classe=classe)

    return render(request, 'prof/classe.html', {'professor': professor ,'classe':classe, 'projects':projects})

def add_project(request, class_id):
    classe = Classe.objects.get(id=class_id)

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
                messages.success(request, "Projet ajouté avec succès !")
                
            except Exception as e:
                print(f"Error: {e}")
                messages.error(request, f"Erreur lors de l'ajout du projet: {e}")

            return redirect('classe_detail', class_id=classe.id)

    return render(request, 'prof/classe.html', {'classe': classe})


def projet_detail(request, projet_id):
    projet = get_object_or_404(Project, id=projet_id)
    instructions = projet.instructions.all()  # Fetch all instructions for this project
    total_groups_count = Groupe.objects.filter(projet=projet).count()
    instruction_stats = []
    for instruction in instructions:
        if InstructionStatus.objects.filter(instruction=instruction).exists():
            completed_groups_count = InstructionStatus.objects.filter(
                instruction=instruction, est_termine=True
            ).count()
            pending_groups_count = total_groups_count - completed_groups_count
            

        else:
            completed_groups_count = 0
            pending_groups_count = total_groups_count

        instruction_stats.append({
            'instruction': instruction,
            'completed_groups': completed_groups_count,
            'pending_groups': pending_groups_count,
            'total_groups': total_groups_count
        })

    total_instructions = len(instruction_stats)
    completed_instructions = sum(1 for stat in instruction_stats if stat['completed_groups'] == stat['total_groups'] and stat['total_groups']>0)
    pending_instructions = total_instructions - completed_instructions
    completion_percentage = (completed_instructions / total_instructions) * 100 if total_instructions else 0

    return render(request, 'prof/projet.html', {
        'projet': projet,
        'total_instructions': total_instructions,
        'instruction_stats': instruction_stats,
        'completed_instructions': completed_instructions,
        'pending_instructions': pending_instructions,
        'completion_percentage': completion_percentage
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
        return redirect('projet_detail', projet_id=projet.id)

    return JsonResponse({"error": "Invalid request"}, status=400)


def prof_notification(request):
    return render(request, 'prof/notification.html')

def prof_profile(request):
    return render(request, 'prof/profile.html')


def prof_settings(request):
    return render(request, 'prof/settings.html')


def prof_calender(request):
    return render(request, 'prof/calender.html')

