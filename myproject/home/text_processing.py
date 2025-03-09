import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet
import string  # Import the string module

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