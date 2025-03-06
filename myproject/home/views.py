from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from .models import TextEntry
from .forms import UserRegistrationForm

@login_required
def home_view(request):
    if request.method == 'POST':
        text_input = request.POST.get('text', '')
        reflection_text = request.POST.get('reflection', '')
        
        if reflection_text:
            TextEntry.objects.create(text=reflection_text, user=request.user)
            return redirect('home')
    return render(request, 'home/index.html')

def analytics(request):
    return render(request, 'home/analytics.html')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect('home')
        else:
            messages.error(request, "Registration failed. Please check your input.")
    else:
        form = UserRegistrationForm()
    return render(request, 'home/register.html', {"form": form})