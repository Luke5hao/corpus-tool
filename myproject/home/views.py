from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from .models import TextEntry, UserProfile
from .forms import UserRegistrationForm
from collections import Counter
import re
from .text_processing import tokenize_and_clean
from .text_processing import compute_keyness
from .analysis import perform_analysis

@login_required
def home_view(request):
    if request.method == 'POST':
        worklog_link = request.POST.get('worklog', '')
        reflection_text = request.POST.get('reflection', '')
        
        if reflection_text:
            # Process text once and store results
            processed_text = tokenize_and_clean(reflection_text)
            
            # Create database entry with the current reflection and capture the instance
            current_entry = TextEntry.objects.create(
                text=reflection_text, 
                worklog=worklog_link,
                user=request.user,
                processed_text=processed_text
            )

            # Generate word frequencies from the current submission (target)
            words = processed_text.split()
            target_frequencies = dict(sorted(Counter(words).items(), 
                                  key=lambda x: (-x[1], x[0])))
            
            # Gather all previous entries from the user (exclude the current one) for the reference corpus
            user_entries = TextEntry.objects.filter(user=request.user).exclude(id=current_entry.id)
            reference_text = ' '.join(entry.processed_text for entry in user_entries)
            reference_words = reference_text.split()
            reference_frequencies = dict(sorted(Counter(reference_words).items(), 
                                      key=lambda x: (-x[1], x[0])))

            # Store frequencies and sizes in session
            request.session['target_frequencies'] = target_frequencies
            request.session['reference_frequencies'] = reference_frequencies
            request.session['target_size'] = len(words)
            request.session['reference_size'] = len(reference_words)
            
            return redirect('analytics')
            
    return render(request, 'home/index.html')

@login_required
def analytics(request):
    compare_to = request.GET.get('compare_to', 'reference')

    target_frequencies = request.session.get('target_frequencies', {})
    target_size = request.session.get('target_size', 0)
    
    reference_frequencies = request.session.get('reference_frequencies', {})
    reference_size = request.session.get('reference_size', 0)

    target_frequencies, keyness_table = perform_analysis(compare_to, request, request.user)

    # if target_frequencies and reference_frequencies:
    #     keyness_df = compute_keyness(target_frequencies, reference_frequencies, target_size, reference_size)
    #     keyness_table = keyness_df.to_html(index=False)
    # else:
    #     keyness_table = "<p>No data available to compute keyness.</p>"

    return render(request, 'home/analytics.html', {
        'compare_to': compare_to,
        'word_frequencies': target_frequencies,
        'keyness_table': keyness_table
    })

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create UserProfile with class ID
            UserProfile.objects.create(
                user=user,
                class_id=form.cleaned_data['class_id']
            )
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect('home')
        else:
            messages.error(request, "Registration failed. Please check your input.")
    else:
        form = UserRegistrationForm()
    return render(request, 'home/register.html', {"form": form})
