import nltk
import os

NLTK_DATA = os.getenv("NLTK_DATA")
print("--------------------- NTLK Data: --------------------", NLTK_DATA)

nltk.download('punkt', download_dir=NLTK_DATA)
nltk.download('averaged_perceptron_tagger', download_dir=NLTK_DATA)
nltk.download('wordnet', download_dir=NLTK_DATA)
# Downlaod the averaged_perceptron_tagger_eng package
nltk.download('averaged_perceptron_tagger_eng', download_dir=NLTK_DATA)
