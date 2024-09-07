import nltk
import os

# Set the download directory to one of the paths NLTK searches
nltk_data_path = '/home/ubuntu/nltk_data'

# Create the directory if it doesn't exist
if not os.path.exists(nltk_data_path):
    os.makedirs(nltk_data_path)

# Download the 'punkt' tokenizer to the specified directory
nltk.download('punkt', download_dir=nltk_data_path)

# Add the download directory to the NLTK data path (if necessary)
nltk.data.path.append(nltk_data_path)

# Now you can use nltk with 'punkt' tokenizer
from nltk.tokenize import word_tokenize

text = "Hello, how are you?"
tokens = word_tokenize(text)
print(tokens)
