import os

# Access the environment variables
PUBMED_API_KEY = os.environ.get("PUBMED_API_KEY")
PUBMED_BASE_URL = os.environ.get("PUBMED_BASE_URL")
PUBMED_SEARCH_STRATEGY_2014_to_2017 = os.environ.get("PUBMED_SEARCH_STRATEGY_2014_to_2017")
PUBMED_SEARCH_STRATEGY_2018_to_2020 = os.environ.get("PUBMED_SEARCH_STRATEGY_2018_to_2020")
PUBMED_SEARCH_STRATEGY_2021_to_2024 = os.environ.get("PUBMED_SEARCH_STRATEGY_2021_to_2024")

# Database parameters
#DIRENV_DIR = os.environ.get("DIRENV_DIR")
#DATA_DIRECTORY = f"{DIRENV_DIR[1:]}/data" #the slice is for removing the first dash
#DATABASE_PATH = f"{DIRENV_DIR[1:]}/data/MethodMIND.db"

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
