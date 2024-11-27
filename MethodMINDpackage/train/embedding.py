from transformers import AutoModel, AutoTokenizer
import torch
from chunking import chunking
from PubMed import get_pubmed_data


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


def store_chunk_embeddings():
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

            # Embed the text using the reusable embed_text function
            embedding = embed_text(text)

            # Store the embedding and metadata
            group_embeddings.append({
                "embedding": embedding,
                "metadata": metadata
            })

        # Append the group of embeddings with metadata
        embedded_chunks_with_metadata.append(group_embeddings)

    # Return the final list of embeddings with metadata
    return embedded_chunks_with_metadata


# test
embedded_chunks_with_metadata = store_chunk_embeddings()
print(embedded_chunks_with_metadata)
