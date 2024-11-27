import requests
import xml.etree.ElementTree as ET
import pandas as pd
from MethodMINDpackage.params import PUBMED_API_KEY, PUBMED_BASE_URL, PUBMED_SEARCH_STRATEGY


def get_pubmed_data():
    '''This function call the pubmed api and return the abtracts and its metadata in a dataframe'''

    # Step 1: Search for articles using ESearch
    search_params = {
        "db": "pubmed",
        "term": PUBMED_SEARCH_STRATEGY,
        "retmax": 10,  # Number of results to retrieve
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

    # Extract Title, Abstract, DOI, Keywords, and Publication Date
    for article in root.findall(".//PubmedArticle"):
        title = article.find(".//ArticleTitle").text
        abstract = article.find(".//AbstractText")
        doi = None
        for id_elem in article.findall(".//ArticleId"):
            if id_elem.get("IdType") == "doi":
                doi = id_elem.text

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

        # Append the extracted data to the list
        data.append({
            "Title": title,
            "Abstract": abstract.text if abstract is not None else None,
            "DOI": doi,
            "Keywords": ", ".join(keywords) if keywords else None,
            "Publication Date": pub_date
        })

    # Create a DataFrame from the collected data
    df = pd.DataFrame(data)

    return df

print(get_pubmed_data())
