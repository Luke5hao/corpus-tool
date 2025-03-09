from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from .models import TextEntry
from .forms import UserRegistrationForm
from collections import Counter
import re
from .text_processing import tokenize_and_clean

@login_required
def home_view(request):
    if request.method == 'POST':
        text_input = request.POST.get('text', '')
        reflection_text = request.POST.get('reflection', '')
        
        if reflection_text:
            TextEntry.objects.create(text=reflection_text, user=request.user)

            processed_text = tokenize_and_clean(reflection_text)
            words = processed_text.split()  # Split processed text into words
            word_frequencies = dict(Counter(words))
            word_frequencies = dict(sorted(word_frequencies.items(), 
                            key=lambda x: (-x[1], x[0])))
        
            request.session['word_frequencies'] = word_frequencies
            return redirect('analytics')
    return render(request, 'home/index.html')

def analytics(request):
    word_frequencies = request.session.get('word_frequencies', {})
    return render(request, 'home/analytics.html', {
        'word_frequencies': word_frequencies
    })

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