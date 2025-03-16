import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet
import string
import numpy as np
from scipy import stats
import pandas as pd

nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger_eng')

def get_wordnet_pos(nltk_tag):
    """Convert NLTK POS tags to WordNet POS tags for lemmatization."""
    if nltk_tag.startswith('J'):
        return wordnet.ADJ
    elif nltk_tag.startswith('V'):
        return wordnet.VERB
    elif nltk_tag == 'VBG':  # Gerund/present participle
        return wordnet.VERB
    elif nltk_tag == 'NN' or nltk_tag == 'NNS':  # singular or plural noun
        return wordnet.NOUN
    elif nltk_tag.startswith('N'):
        return wordnet.NOUN
    elif nltk_tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN

def tokenize_and_clean(text, remove_stop=True, do_lemmatize=True):
    stop_words = set(stopwords.words('english'))
    # Add punctuation to stop words
    stop_words.update(string.punctuation)  
    lemmatizer = WordNetLemmatizer()
    
    # Tokenize text properly (word_tokenize handles punctuation better)
    tokens = word_tokenize(text.lower())

    # Get POS tags
    pos_tags = nltk.pos_tag(tokens)

    cleaned = []
    for token, tag in pos_tags:
        if remove_stop and token in stop_words:
            continue
        if do_lemmatize:
            wordnet_pos = get_wordnet_pos(tag)  # Get WordNet POS
            token = lemmatizer.lemmatize(token, wordnet_pos)
        cleaned.append(token)
    
    return ' '.join(cleaned)

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