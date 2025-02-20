from django.shortcuts import render, redirect
from .models import TextEntry

def home_view(request):
    if request.method == 'POST':
        print("POST data received:", request.POST)  # Debugging line
        text_input = request.POST.get('text', '')
        if text_input:
            TextEntry.objects.create(text=text_input)
            return redirect('home')
    return render(request, 'home/index.html')