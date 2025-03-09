from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from .models import TextEntry
from .forms import UserRegistrationForm
from collections import Counter
import re
from .text_processing import tokenize_and_clean
import numpy as np
from scipy import stats
import pandas as pd

@login_required
def home_view(request):
    if request.method == 'POST':
        text_input = request.POST.get('text', '')
        reflection_text = request.POST.get('reflection', '')
        
        if reflection_text:
            # Process text once and store results
            processed_text = tokenize_and_clean(reflection_text)
            
            # Create database entry with the current reflection and capture the instance
            current_entry = TextEntry.objects.create(
                text=reflection_text, 
                user=request.user,
                processed_text=processed_text  # Assuming you have this field
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
    target_frequencies = request.session.get('target_frequencies', {})
    reference_frequencies = request.session.get('reference_frequencies', {})
    target_size = request.session.get('target_size', 0)
    reference_size = request.session.get('reference_size', 0)

    if target_frequencies and reference_frequencies:
        keyness_df = compute_keyness(target_frequencies, reference_frequencies, target_size, reference_size)
        keyness_table = keyness_df.to_html(index=False)
    else:
        keyness_table = "<p>No data available to compute keyness.</p>"

    return render(request, 'home/analytics.html', {
        'word_frequencies': target_frequencies,
        'keyness_table': keyness_table
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

def compute_keyness(target_freq, reference_freq, target_size, reference_size):
    """
    Computes keyness scores and significance (p-values) for words in a target corpus.
    
    Parameters:
    - target_freq (dict): Word frequencies in the target corpus {word: count}.
    - reference_freq (dict): Word frequencies in the reference corpus {word: count}.
    - target_size (int): Total word count in the target corpus.
    - reference_size (int): Total word count in the reference corpus.
    
    Returns:
    - DataFrame with columns: ['word', 'freq_target', 'freq_reference', 'keyness', 'p_value']
    """
    results = []

    all_words = set(target_freq.keys()).union(reference_freq.keys())

    for word in all_words:
        O1 = target_freq.get(word, 0)  # Observed frequency in target
        O2 = reference_freq.get(word, 0)  # Observed frequency in reference

        # Expected frequencies based on corpus sizes
        E1 = (O1 + O2) * (target_size / (target_size + reference_size))
        E2 = (O1 + O2) * (reference_size / (target_size + reference_size))

        # Compute each log-likelihood component separately
        first_term = (O1 * np.log(O1 / E1)) if O1 > 0 else 0
        second_term = (O2 * np.log(O2 / E2)) if O2 > 0 else 0
        G = 2 * (first_term + second_term)

        # Optionally, assign a sign based on whether the target frequency is higher or lower than expected.
        # For example, use positive G if O1 >= E1, negative otherwise.
        signed_G = G if O1 >= E1 else -G

        # Compute p-value for significance (always uses the absolute G)
        p_value = 1 - stats.chi2.cdf(abs(G), df=1)

        results.append((word, O1, O2, signed_G, p_value))

    # Convert to a DataFrame
    df = pd.DataFrame(results, columns=['word', 'freq_target', 'freq_reference', 'keyness', 'p_value'])
    df = df.sort_values(by='p_value', ascending=True)

    return df