from django.shortcuts import render

def policy(request):
    return render(request, 'policy.html')

def delete(request):
    return render(request, 'delete.html')