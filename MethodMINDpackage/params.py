import os

# Access the environment variables
PUBMED_API_KEY = os.environ.get("PUBMED_API_KEY")
PUBMED_BASE_URL = os.environ.get("PUBMED_BASE_URL")
PUBMED_SEARCH_STRATEGY = os.environ.get("PUBMED_SEARCH_STRATEGY")

# Database parameters
DIRENV_DIR = os.environ.get("DIRENV_DIR")
DATA_DIRECTORY = f"{DIRENV_DIR[1:]}/data" #the slice is for removing the first dash

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
