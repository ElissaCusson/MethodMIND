import google.generativeai as genai
from transformers import AutoModel, AutoTokenizer
from MethodMINDpackage.params import GEMINI_API_KEY, PUBMED_API_KEY
from pymilvus import Collection
from MethodMINDpackage.train.database import connectDB_alias, disconnect_alias
import requests
import xml.etree.ElementTree as ET

def user_input_enhancing(user_input):
    """
    Enhances user input by generating a hypothetical abstract using Gemini LLM,
    chunking the abstract, and embedding the chunks using SciBERT.
    """
    if user_input is None or not user_input.strip():
        return "Please enter a valid question."

    # Query enhancing: generate a hypothetical abstract using Gemini LLM
    # Initialize the Gemini LLM
    genai.configure(api_key=GEMINI_API_KEY)
    llm = genai.GenerativeModel(model_name="gemini-1.5-flash")

    # Define the prompt
    prompt = (
        f"Generate a detailed abstract based on the following user query, adhering to the IMRaD structure (Introduction, Methods, Results, and Discussion/Conclusion):\n\n"
        f"User query: {user_input}\n\n"
        f"Abstract:"
    )

    # Generate the hypothetical abstract
    hypothetical_abstract = llm.generate_content(prompt).text

    # Ensure the hypothetical abstract is valid
    if not hypothetical_abstract or not hypothetical_abstract.strip():
        return "Failed to generate a valid hypothetical abstract."

    return hypothetical_abstract

def test_embedding(query):
    # Embed the chunks using SciBERT
    # Load SciBERT model and tokenizer
    model_name = "allenai/scibert_scivocab_uncased"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)

    # Tokenize the chunk text
    inputs = tokenizer(query, return_tensors="pt", padding=True, truncation=True, max_length=512)
    output = model(**inputs)
    embedding = output.last_hidden_state.mean(dim=1).detach().squeeze().numpy()
    return embedding

def search_similarity(query, k=30):
    """Takes raw text (base query) and returns a nested list [data: ["['id: ..., distance: ..., entity: {}', ...]], True]"""
    if query is None or not query.strip():
        return [None, False, "Query is required."]
    # client=connectDB()
    client_alias = connectDB_alias()

    if client_alias is None:
        print("Failed to connect to the database.")
        return [None, False, "Failed to connect to the database."]
    collection = Collection(name="MethodVectors", using=client_alias)

    # Get the query embedding
    query_embedding = test_embedding(query)

    results = collection.search(
        data=[query_embedding],
        anns_field="embedding",
        param={"metric_type": "COSINE", "params": {"nprobe": 50}},  # You can adjust metric_type and nprobe as needed
        limit=k,
        expr=None  # You can add filtering expressions here if needed
    )
    disconnect_alias(client_alias)
    return [results, True]

def query_by_id(set_query_ids=None):
    """
    Retrieve metadata for a list of IDs from the collection.

    Args:
        set_query_ids: A set of the ID to search for.

    Returns:
        nested list: Query results containing matched metadata and vector data.
    """
    metadata_list = []
    for query_id in set_query_ids:
        if query_id is None:
            print("Query ID is required.")
            return [None, False, "Query ID is required."]

        # Connect and load the collection
        client_alias = connectDB_alias()
        if client_alias is None:
            print("Failed to connect to the database.")
            return [None, False, "Failed to connect to the database."]

        collection = Collection(name="MethodVectors", using=client_alias)

        # Build filter expression for ID
        filter_expression = f"id == {query_id}"

        # Perform the query using Collection.query()
        try:
            results = collection.query(
                expr=filter_expression,  # Filter by ID
                output_fields=["title", "doi", "keywords", "full_text_link", "publication_date"]  # Specify fields to retrieve
            )
            print(f"Query completed. Retrieved {len(results)} results.")
            metadata_list.append(results)
        except Exception as e:
            print(f"An error occurred during query: {e}")
            return [None, False, f"An error occurred during query: {e}"]
        finally:
            # Always disconnect after query
            disconnect_alias()
    return [metadata_list, True]

def get_abstract_by_doi(metadata_list):
    api_key = PUBMED_API_KEY  # Ensure you have your API key available
    for metadata in metadata_list:
        doi = metadata[0].get('doi')  # Get the DOI from the metadata dictionary
        if doi is None:
            metadata[0]['abstract'] = None
            continue

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
            metadata[0]['abstract'] = 'NR'  # No record found
            continue

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
        abstract_elems = root.findall(".//AbstractText")
        if abstract_elems:
            full_abstract = " ".join([elem.text for elem in abstract_elems if elem.text])
            metadata[0]['abstract'] = full_abstract

        else:
            metadata[0]['abstract'] = 'NR'  # If no abstract found

    return [metadata_list, True]  # Return the modified list of metadata dictionaries

def handle_multiple_similarities(best_matches):
    """ Gets a list of the most similar chunks and returns a set of abstract IDs"""
    return set([match.id for match in best_matches])

if __name__=='__main__':
    pass

    ########### MVP TEST
    #user_query = ''
    user_query = "Which methods can I use to measure tremor decrease and gait improvement in Parkinson patients receiving deep brain stimulation?"

    ###############

    # # Display the most similar document
    similarity = search_similarity(user_query, k=10)
    print(similarity)

    # Multiple similarity test:
    multiple_similarities = handle_multiple_similarities(similarity[0][0])
    # print(multiple_similarities)

    # # query by id tests:
    ids=query_by_id(set_query_ids=multiple_similarities)
    # print(ids)

    print(get_abstract_by_doi(metadata_list = ids[0]))
