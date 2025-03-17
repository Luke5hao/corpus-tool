from .models import TextEntry, UserProfile
from .text_processing import tokenize_and_clean
from .text_processing import compute_keyness
from collections import Counter

def perform_analysis(compare_to, request, user):
  # RETRIEVE MOST-RECENT USER ENTRY AND CALCULATE TARGET STATS
  try:
    most_recent_entry = TextEntry.objects.filter(user=request.user).latest('created_at')
    most_recent_entry_id = most_recent_entry.id
    target_frequencies = most_recent_entry.processed_text.split()
    target_frequencies = dict(sorted(Counter(target_frequencies).items(), key=lambda x: (-x[1], x[0])))
    target_size = len(target_frequencies)
  except TextEntry.DoesNotExist:
    most_recent_entry = TextEntry.objects.none()
    most_recent_entry_id = None
    target_frequencies = {}
    target_size = 0


  # CALCULATE REFERENCE STATS
  reference_frequencies = {}
  reference_size = 0

  if compare_to == 'class':
    # Fetch data for users with same class ID (excluding the current user)
    try:
      user_class_id = user.userprofile.class_id
      if user_class_id:
        user_entries = TextEntry.objects.filter(
          user__userprofile__class_id=user_class_id).exclude(user=user)
      else:
        user_entries = TextEntry.objects.none()
    except AttributeError: # Catches users who don't have a class ID
      user_entries = TextEntry.objects.none()
  elif compare_to == 'previous':
    # Gather all entries from the user (excluding the most recent entry)
    user_entries = TextEntry.objects.filter(user=request.user).exclude(
              id=most_recent_entry_id)
  elif compare_to == 'all':
    # Fetch data for all users (excluding the current user)
    user_entries = TextEntry.objects.exclude(user=user)
  elif compare_to == 'michigan':
    # Fetch data for Michigan Corpus (need to upload/identify these entries)
    user_entries = TextEntry.objects.filter(is_michigan_corpus=True)
  else:
    user_entries = TextEntry.objects.none()

  # Process reference entries
  reference_text = ' '.join(entry.processed_text for entry in user_entries)
  reference_words = reference_text.split()
  reference_frequencies = dict(sorted(Counter(reference_words).items(), key=lambda x: (-x[1], x[0])))
  reference_size = len(reference_words)


  # STORE FREQ/SIZE DATA IN SESSION
  request.session['target_frequencies'] = target_frequencies
  request.session['reference_frequencies'] = reference_frequencies
  request.session['target_size'] = target_size
  request.session['reference_size'] = reference_size


  # PROCESS TEXT
  if target_frequencies and reference_frequencies:
    keyness_df = compute_keyness(target_frequencies, reference_frequencies, target_size, reference_size)
    keyness_table = keyness_df.to_html(index=False)
  else:
    keyness_table = "<p>No data available to compute keyness.</p>"
  
  return target_frequencies, keyness_table

    