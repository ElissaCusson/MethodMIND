from transformers import AutoModel, AutoTokenizer
import torch
from chunking import chunking
from database import disconnect_client
from PubMed import get_pubmed_data, get_pubmed_data_by_year
from pymilvus import MilvusClient
from MethodMINDpackage.params import *

# Load SciBERT model and tokenizer once globally
model_name = "allenai/scibert_scivocab_uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

def embed_text(text):
    '''This function vectorizes text using the preloaded SciBERT model.'''
    # Tokenize the input text
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)

    # Pass through the model
    with torch.no_grad():
        outputs = model(**inputs)

    # Extract the embeddings (mean pooling over token embeddings)
    embeddings = outputs.last_hidden_state.mean(dim=1)

    return embeddings

def store_chunk_embeddings(client, collection_name):
    """Store the embeddings for each chunk along with metadata."""
    # Process abstracts_chunked
    abstracts_chunked = chunking(df=get_pubmed_data(), chunk_size=100, chunk_overlap=20)

    # List to hold embeddings with metadata
    embedded_chunks_with_metadata = []

    # Iterate over the chunks and their metadata
    for chunk_group in abstracts_chunked:
        for chunk in chunk_group:
            # Extract text and metadata
            text = chunk.page_content
            metadata = chunk.metadata

            # Embed the text
            embedding = embed_text(text).squeeze(0).numpy()

            # Store the embedding and metadata
            group_embeddings = {
                "embedding": embedding,
                "title": metadata['Title'],
                "doi": metadata['DOI'],
                "keywords": metadata['Keywords'],
                "publication_date": metadata['Publication Date'],
                "full_text_link": metadata['Full Text Link']
            }

            # Insert into Milvus
            client.insert(collection_name=collection_name, data=[group_embeddings])

        print(f"Inserted {len(group_embeddings)} embeddings into collection {collection_name}.")

        # Append the group of embeddings with metadata
        embedded_chunks_with_metadata.append(group_embeddings)

    # Return the final list of embeddings with metadata
    return embedded_chunks_with_metadata

def store_abstracts_embeddings(client, collection_name):
    # all 3 get pubmed data
    df = get_pubmed_data(PUBMED_SEARCH_STRATEGY_2014_to_2017)
    # Filter out rows where Abstract is None or empty
    df = df[df['Abstract'].notna() & (df['Abstract'].str.strip() != '')]

    abstracts_list = df['Abstract'].to_list()

    # Iterate through each abstract and corresponding metadata
    for i, abstract in enumerate(abstracts_list):
        # Embed the abstract text
        embedding = embed_text(abstract).squeeze(0).numpy()

        # Store the embedding and metadata together
        group_embeddings = {
            "embedding": embedding,
            "title": df.iloc[i]['Title'],
            "doi": df.iloc[i]['DOI'],
            "keywords": df.iloc[i]['Keywords'],
            "publication_date": df.iloc[i]['Publication Date'],
            "full_text_link": df.iloc[i]['Full Text Link']
        }

        # Insert into Milvus
        client.insert(collection_name=collection_name, data=[group_embeddings], progress_bar=True)
        print(f"Inserted abstract {i} into collection {collection_name}.")
    return print('Embedded abstracts added in Milvus')

if __name__=='__main__':
    pass
    # connect to Milvus
    database_name="MethodMIND"
    client = MilvusClient(uri=DATABASE_PATH)  # Initialize MilvusClient
    collection_name = "MethodVectors"

    # test connect to collection
    if collection_name in client.list_collections():
        print(f"Collection {collection_name} already exists...")
    else:
        print("No collection")
    # Store embeddings in Milvus
    #store_chunk_embeddings(client, collection_name) # chunk embeddings
    store_abstracts_embeddings(client, collection_name) # abstract embeddings

    row_count = client.get_collection_stats(collection_name=collection_name)['row_count']
    print(f"\n {database_name} database as {row_count} in collection {collection_name}")

    disconnect_client(client, collection_name="MethodVectors")
