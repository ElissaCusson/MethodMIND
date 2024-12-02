import requests
import xml.etree.ElementTree as ET
import pandas as pd
from MethodMINDpackage.params import *

def get_pubmed_data():
    '''This function calls the PubMed API and returns abstracts, metadata, and full-text links in a DataFrame'''

    # Step 1: Search for articles using ESearch
    search_params = {
        "db": "pubmed",
        "term": PUBMED_SEARCH_STRATEGY_2021_to_2024,
        "retmax": 9999,  # Number of results to retrieve
        "retmode": "json",
        "api_key": PUBMED_API_KEY
    }
    esearch_url = f"{PUBMED_BASE_URL}esearch.fcgi"
    search_response = requests.get(esearch_url, params=search_params)

    # Parse the article IDs
    article_ids = search_response.json()["esearchresult"]["idlist"]
    if not article_ids:
        print("No article IDs found. Check your search parameters.")
        return pd.DataFrame()

    print(f"Fetched {len(article_ids)} Article IDs.")

    # Step 2: Fetch detailed information using EFetch in smaller batches
    batch_size = 100  # Set the batch size
    data = []  # List to store all articles' data

    # Split the article_ids into batches
    for i in range(0, len(article_ids), batch_size):
        batch_ids = article_ids[i:i + batch_size]
        efetch_params = {
            "db": "pubmed",
            "id": ",".join(batch_ids),
            "retmode": "xml",
            "api_key": PUBMED_API_KEY
        }
        efetch_url = f"{PUBMED_BASE_URL}efetch.fcgi"
        fetch_response = requests.get(efetch_url, params=efetch_params)

        # Log the response content
        print(f"Response from PubMed EFetch (Batch {i // batch_size + 1}): {fetch_response.text[:500]}")  # Show first 500 characters of the response

        # Validate the response content
        if not fetch_response.content.strip():
            print("Empty response received from PubMed EFetch for this batch.")
            continue  # Skip this batch and proceed to the next one

        try:
            # Parse the XML response
            root = ET.fromstring(fetch_response.content)
        except ET.ParseError as e:
            print(f"XML Parse Error in batch {i // batch_size + 1}: {e}. Response: {fetch_response.content}")
            continue  # Skip this batch and proceed to the next one

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

            # Only add articles with a non-null Abstract and DOI
            if abstract is not None and doi is not None:
                data.append({
                    "Title": title if title is not None else "NR",
                    "Abstract": abstract.text,
                    "DOI": doi,
                    "Full Text Link": full_text_link if full_text_link is not None else "NR",
                    "Keywords": ", ".join(keywords) if keywords else "NR",
                    "Publication Date": pub_date if pub_date is not None else "NR"
                })

    # Create a DataFrame from the collected data
    df = pd.DataFrame(data)

    return df

if __name__=='__main__':
    pass
    # # Test the function
    # print(get_pubmed_data())
