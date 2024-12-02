import requests
import xml.etree.ElementTree as ET
import pandas as pd
from MethodMINDpackage.params import PUBMED_API_KEY, PUBMED_BASE_URL, PUBMED_SEARCH_STRATEGY
from MethodMINDpackage.orchestraDitector.retrival import query_by_id

########### MVP TEST
user_query = "Which methods can I use to measure tremor decrease and gait improvement in Parkinson patients receiving deep brain stimulation?"
###############

def get_pubmed_data():
    '''This function calls the PubMed API and returns abstracts, metadata, and full-text links in a DataFrame'''

    # Step 1: Search for articles using ESearch
    search_params = {
        "db": "pubmed",
        "term": PUBMED_SEARCH_STRATEGY,
        "retmax": 100,  # Number of results to retrieve
        "retmode": "json",
        "api_key": PUBMED_API_KEY
    }
    esearch_url = f"{PUBMED_BASE_URL}esearch.fcgi"
    search_response = requests.get(esearch_url, params=search_params)

    # Parse the article IDs
    article_ids = search_response.json()["esearchresult"]["idlist"]
    print("Article IDs:", article_ids)

    # Step 2: Fetch detailed information using EFetch
    efetch_params = {
        "db": "pubmed",
        "id": ",".join(article_ids),
        "retmode": "xml",
        "api_key": PUBMED_API_KEY
    }
    efetch_url = f"{PUBMED_BASE_URL}efetch.fcgi"
    fetch_response = requests.get(efetch_url, params=efetch_params)

    # Parse the XML response
    root = ET.fromstring(fetch_response.content)

    # Prepare a list to store extracted data
    data = []

    # Extract Title, Abstract, DOI, Keywords, Publication Date, and Full-Text Link
    for article in root.findall(".//PubmedArticle"):
        title = article.find(".//ArticleTitle").text
        abstract = article.find(".//AbstractText")
        doi = None
        full_text_link = None

        # Extract DOI and Full-Text Link
        for id_elem in article.findall(".//ArticleId"):
            if id_elem.get("IdType") == "doi":
                doi = id_elem.text
                full_text_link = f"https://doi.org/{doi}"  # Construct full-text link from DOI

        # Extract keywords
        keywords = [kw.text for kw in article.findall(".//Keyword") if kw.text is not None]

        # Extract publication date
        date_elem = article.find(".//DateCompleted")  # Prefer DateCompleted if available
        if date_elem is None:
            date_elem = article.find(".//ArticleDate")  # Use ArticleDate as a fallback

        if date_elem is not None:
            pub_date = "-".join([
                date_elem.find("Year").text,
                date_elem.find("Month").text.zfill(2),  # Ensure two-digit month
                date_elem.find("Day").text.zfill(2)  # Ensure two-digit day
            ])
        else:
            pub_date = None

        # Only add articles with a non-null Abstract
        if abstract is not None:
            data.append({
                "Title": title if title is not None else "NR",
                "Abstract": abstract.text,
                "DOI": doi if doi is not None else "NR",
                "Full Text Link": full_text_link if full_text_link is not None else "NR",
                "Keywords": ", ".join(keywords) if keywords else "NR",
                "Publication Date": pub_date if pub_date is not None else "NR"
            })

    # Create a DataFrame from the collected data
    df = pd.DataFrame(data)

    return df

import requests
import xml.etree.ElementTree as ET
def get_abstract_by_doi(user_query, doi= None):
    doi = query_by_id(user_query, query_id=None)
    api_key=PUBMED_API_KEY
    # Step 1: Search for the article using ESearch to get the PubMed ID (PMID) from the DOI
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    search_params = {
        "db": "pubmed",
        "term": f"doi:{doi}",  # Search for the DOI
        "retmode": "json",
        "api_key": api_key
    }
    search_response = requests.get(search_url, params=search_params)
    search_data = search_response.json()
    # Check if a PMID was found for the DOI
    if "idlist" not in search_data["esearchresult"] or not search_data["esearchresult"]["idlist"]:
        print("No article found for the given DOI.")
        return None
    pmid = search_data["esearchresult"]["idlist"][0]  # Get the first PMID
    # Step 2: Fetch article details using EFetch
    efetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    efetch_params = {
        "db": "pubmed",
        "id": pmid,
        "retmode": "xml",
        "api_key": api_key
    }
    fetch_response = requests.get(efetch_url, params=efetch_params)
    # Parse the XML response
    root = ET.fromstring(fetch_response.content)
    # Extract the abstract
    abstract_elem = root.find(".//AbstractText")
    if abstract_elem is not None:
        return abstract_elem.text
    else:
        print("No abstract found for the given DOI.")
        return None

##############
#print(get_abstract_by_doi(user_query, doi= None))
# Example usage
# doi = "10.3390/nu16223863"  # Replace with a valid DOI
# api_key = "781f1d6e9a1ddd33b37d1ef4facf505a7209"  # Replace with your PubMed API key
# abstract = get_abstract_by_doi(doi, api_key)
# if abstract:
#     print("Abstract:", abstract)

# # Test the function
# print(get_pubmed_data())
