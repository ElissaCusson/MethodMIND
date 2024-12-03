from transformers import T5Tokenizer, AutoModelForSeq2SeqLM

def reranking(user_input, metadata_list, n_results=5):
    model_name = "castorini/monot5-base-msmarco"
    tokenizer = T5Tokenizer.from_pretrained(model_name)  # Use T5Tokenizer here
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    # Rerank each document
    ranked_results = []
    for metadata in metadata_list:
        abstract = metadata[0].get('abstract', '')  # Extract abstract from metadata
        if not abstract:  # Skip if abstract is missing or empty
            continue

        # Prepare input text
        input_text = f"Query: {user_input} Document: {abstract}"

        # Tokenize input text
        inputs = tokenizer(input_text, return_tensors="pt", padding=True, truncation=True, max_length=512)

        # Generate model outputs
        outputs = model.generate(**inputs)

        # Decode the generated tokens to get relevance score or output
        relevance_score = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Add abstract and relevance score to ranked results
        ranked_results.append((abstract, relevance_score))

    # Sort documents by relevance score (numerical comparison may be necessary)
    ranked_results = sorted(ranked_results, key=lambda x: x[1], reverse=True)

    # Get the top 'n_results' best documents with their relevance score
    top_ranked = ranked_results[:n_results]

    # Create a new metadata list with only the top n_results and their relevance score
    final_metadata_list = []
    for metadata, relevance_score in top_ranked:
        metadata[0]['relevance_score'] = relevance_score  # Add relevance score to the metadata
        final_metadata_list.append(metadata)

    return final_metadata_list
