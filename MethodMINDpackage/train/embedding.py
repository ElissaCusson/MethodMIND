from transformers import AutoModel, AutoTokenizer
import torch
from chunking import chunking
from PubMed import get_pubmed_data
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


# connect to Milvus
database_name="MethodMIND"
client = MilvusClient(uri=DATABASE_PATH)  # Initialize MilvusClient
collection_name = "MethodVectors"

# test connect to collection
if collection_name in client.list_collections():
    print(f"Collection {collection_name} already exists...")
else:
    print("No collection")

def store_chunk_embeddings(client, collection_name):
    """Store the embeddings for each chunk along with metadata."""
    # Process abstracts_chunked
    abstracts_chunked = chunking(df=get_pubmed_data(), chunk_size=100, chunk_overlap=20)

    # List to hold embeddings with metadata
    embedded_chunks_with_metadata = []

    # Iterate over the chunks and their metadata
    for chunk_group in abstracts_chunked:
        group_embeddings = []
        for chunk in chunk_group:
            # Extract text and metadata
            text = chunk.page_content
            metadata = chunk.metadata

            # Embed the text
            embedding = embed_text(text)

            # Store the embedding and metadata
            group_embeddings.append({
                "embedding": embedding,
                "title": metadata['Title'],
                "doi": metadata['DOI'],
                "keywords": metadata['Keywords'],
                "publication_date": metadata['Publication Date'],
                "full_text_link": metadata['Full Text Link']
            })

        # Convert group_embeddings into a dictionary of lists for Milvus insertion
        insert_data = [{
            "embedding": [item["embedding"] for item in group_embeddings],
            "title": [item["title"] for item in group_embeddings],
            "doi": [item["doi"] for item in group_embeddings],
            "keywords": [item["keywords"] for item in group_embeddings],
            "publication_date": [item["publication_date"] for item in group_embeddings],
            "full_text_link": [item["full_text_link"] for item in group_embeddings],
        }]

        # Insert into Milvus
        client.insert(collection_name=collection_name, data=insert_data)

        print(f"Inserted {len(group_embeddings)} embeddings into collection {collection_name}.")

        # Append the group of embeddings with metadata
        embedded_chunks_with_metadata.append(group_embeddings)

    # Return the final list of embeddings with metadata
    return embedded_chunks_with_metadata


# Store embeddings in Milvus
store_chunk_embeddings(client, collection_name)

row_count = client.get_collection_stats(collection_name=collection_name)['row_count']
print(f"\n {database_name} database as {row_count} in collection {collection_name}")
