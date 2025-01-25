from django.shortcuts import render

def chat(request):
    return render(request, 'workSpace/chat.html')

def todo(request):
    return render(request, 'workSpace/todo.html')