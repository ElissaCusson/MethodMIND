from chunking import chunking
import torch
from transformers import AutoTokenizer, AutoModel

def embedding():
    """Generates embeddings for a list of text chunks using SciBERT."""
    # Get chunked data
    chunks = chunking()

    # Load the SciBERT model and tokenizer
    model_name = "allenai/scibert_scivocab_cased"
    model = AutoModel.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    # Process each chunk
    embeddings = []
    for chunk in chunks:
        # Tokenize the chunk text
        inputs = tokenizer(chunk, return_tensors="pt", truncation=True, padding=True)

        # Get embeddings using SciBERT
        with torch.no_grad():  # Disable gradient calculations for inference
            outputs = model(**inputs)

        # Extract the embeddings (last hidden state)
        chunk_embeddings = outputs.last_hidden_state.mean(dim=1)  # Average pooling to get 1 embedding per chunk
        embeddings.append(chunk_embeddings)

    return embeddings


print(embedding())
