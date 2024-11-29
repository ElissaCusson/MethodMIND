import requests
import xml.etree.ElementTree as ET
import pandas as pd
from MethodMINDpackage.params import PUBMED_API_KEY, PUBMED_BASE_URL, PUBMED_SEARCH_STRATEGY


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

def get_abstract_text(DOI):
    pass #your code here

# Test the function
print(get_pubmed_data())
