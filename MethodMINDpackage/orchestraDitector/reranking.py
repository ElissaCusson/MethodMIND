from transformers import AutoTokenizer, AutoModelForSeq2SeqLM



def reranking(user_input, metadata_list, n_results = 5):
    # Rerank each document
    ranked_results = []
    for metadata in metadata_list:
        abstract = metadata.get('abstract', '')  # Extract abstract from metadata
        if not abstract:  # Skip if abstract is missing or empty
            continue
        input_text = f"Query: {user_input} Document: {abstract}"
        inputs = tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True)
        outputs = model.generate(**inputs)
        relevance_score = tokenizer.decode(outputs[0], skip_special_tokens=True)
        ranked_results.append((abstract, relevance_score))

    # Sort documents by relevance score (e.g., "true" vs. "false")
    ranked_results = sorted(ranked_results, key=lambda x: x[1], reverse=True)

    # Get the top 'n_results' best documents with their relevance score
    top_ranked = ranked_results[:n_results]

    # Create a new metadata list with only the top n_results and their relevance score
    final_metadata_list = []
    for metadata, relevance_score in top_ranked:
        metadata['relevance_score'] = relevance_score  # Add relevance score to the metadata
        final_metadata_list.append(metadata)

    return final_metadata_list

if __name__ == '__main__':
        # Load monoT5
    model_name = "castorini/monot5-base-msmarco"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
