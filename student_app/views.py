from django.shortcuts import render

def chat(request):
    return render(request, 'workSpace/chat.html')

def todo_ws(request):
    return render(request, 'workSpace/todo.html')

def todo_home(request):
    return render(request, 'home/todo.html')

def calender_home(request):
    return render(request, 'home/calender.html')

def classes(request):
    return render(request, 'home/classes.html')

def notifications(request):
    return render(request, 'home/notifications.html')

def groupes(request):
    return render(request, 'groupes/groupes.html')