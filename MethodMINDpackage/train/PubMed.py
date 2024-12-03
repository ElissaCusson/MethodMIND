import requests
import xml.etree.ElementTree as ET
import pandas as pd
from MethodMINDpackage.params import *

def get_pubmed_data_by_year():
    df1 = get_pubmed_data(PUBMED_SEARCH_STRATEGY_2014_to_2017)
    df2 = get_pubmed_data(PUBMED_SEARCH_STRATEGY_2018_to_2020)
    df3 = get_pubmed_data(PUBMED_SEARCH_STRATEGY_2021_to_2024)
    return  pd.concat([df1, df2, df3], ignore_index=True)

def get_pubmed_data(search_strategy = PUBMED_SEARCH_STRATEGY_2014_to_2017):
    '''This function calls the PubMed API and returns abstracts, metadata, and full-text links in a DataFrame'''
    # Step 1: Search for articles using ESearch
    search_params = {
        "db": "pubmed",
        "term": search_strategy,
        "retmax": 9999,  # Number of results to retrieve
        "retmode": "json",
        "api_key": PUBMED_API_KEY
    }
    esearch_url = f"{PUBMED_BASE_URL}esearch.fcgi"
    search_response = requests.get(esearch_url, params=search_params)

    # Parse the article IDs
    article_ids = search_response.json().get("esearchresult", {}).get("idlist", [])
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

        # Validate the response content
        if not fetch_response.content.strip():
            print(f"Empty response received from PubMed EFetch for batch {i // batch_size + 1}.")
            continue

        try:
            # Parse the XML response
            root = ET.fromstring(fetch_response.content)
        except ET.ParseError as e:
            print(f"XML Parse Error in batch {i // batch_size + 1}: {e}")
            continue

        # Extract Title, Abstract, DOI, Keywords, Publication Date, and Full-Text Link
        for article in root.findall(".//PubmedArticle"):
            title = article.find(".//ArticleTitle")
            title_text = title.text if title is not None else "NR"

            # Extract the abstract
            abstract_elems = article.findall(".//AbstractText")
            abstract = " ".join([elem.text.strip() for elem in abstract_elems if elem.text]) if abstract_elems else "NR"

            # Extract DOI and Full-Text Link
            doi = None
            full_text_link = None
            for id_elem in article.findall(".//ArticleId"):
                if id_elem.get("IdType") == "doi":
                    doi = id_elem.text
                    full_text_link = f"https://doi.org/{doi}" if doi else "NR"

            # Extract keywords
            keywords = [kw.text for kw in article.findall(".//Keyword") if kw.text]

            # Extract publication date
            date_elem = article.find(".//DateCompleted") or article.find(".//ArticleDate")
            if date_elem is not None:
                year = date_elem.find("Year").text if date_elem.find("Year") is not None else "NR"
                month = date_elem.find("Month").text.zfill(2) if date_elem.find("Month") is not None else "NR"
                day = date_elem.find("Day").text.zfill(2) if date_elem.find("Day") is not None else "NR"
                pub_date = f"{year}-{month}-{day}"
            else:
                pub_date = "NR"

            # Only add articles with a non-null Abstract and DOI
            if abstract != "NR" and doi is not None:
                data.append({
                    "Title": title_text,
                    "Abstract": abstract,
                    "DOI": doi,
                    "Full Text Link": full_text_link,
                    "Keywords": ", ".join(keywords) if keywords else "NR",
                    "Publication Date": pub_date
                })

    # Create a DataFrame from the collected data
    df = pd.DataFrame(data)
    print(f"Successfully fetched {len(df)} articles.")
    return df


if __name__=='__main__':
    pass
    # # Test the function
    # Set display options to avoid truncation
    #pd.set_option('display.max_colwidth', None)  # Allows full content in cells
    #pd.set_option('display.max_rows', None)     # Ensures all rows are shown

    # Assuming get_pubmed_data() returns a DataFrame
    #data = get_pubmed_data()
    #print(data['Abstract'])  # View the Abstract column
