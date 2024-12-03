
from transformers import T5Tokenizer, AutoModelForSeq2SeqLM


def reranking(user_input, metadata_list, n_results=5):
    model_name = "castorini/monot5-base-msmarco"
    tokenizer = T5Tokenizer.from_pretrained(model_name)  # Use T5Tokenizer here
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    # Rerank each document
    ranked_results = []
    for metadata in metadata_list:
        abstract = metadata[0].get('abstract', '')  # Extract abstract from metadata
        title = metadata[0].get('title', '')  # Extract title from metadata
        link = metadata[0].get('full_text_link', '')  # Extract link from metadata
        date = metadata[0].get('publication_date', '')  # Extract date from metadata

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

        # Create a dictionary with all the metadata and relevance score
        ranked_results.append({
            'title': title,
            'link': link,
            'date': date,
            'abstract': abstract,
            'relevance_score': relevance_score
        })

    # Sort documents by relevance score (numerical comparison may be necessary)
    ranked_results = sorted(ranked_results, key=lambda x: x['relevance_score'], reverse=True)
    # Get the top 'n_results' best documents with their relevance score
    if n_results > len(ranked_results):
        top_ranked = ranked_results
    else:
        top_ranked = ranked_results[:n_results - 1]

    return top_ranked

if __name__=="__main__":
    pass
    ########### MVP TEST
    # user_query = ''
    # user_query = "Which methods can I use to measure tremor decrease and gait improvement in Parkinson patients receiving deep brain stimulation?"

    # ###############

    # # # Display the most similar document
    # similarity = search_similarity(user_query, k=10)
    # print(similarity)

    # # Multiple similarity test:
    # multiple_similarities = handle_multiple_similarities(similarity[0][0])
    # # print(multiple_similarities)

    # # # query by id tests:
    # ids=query_by_id(set_query_ids=multiple_similarities)
    # # print(ids)

    # dois = set(handle_multiple_metadata(ids[0])['doi'])
    # print(len(dois))
    # # # get_abstract_by_doi tests:
    # abstracts = get_abstract_by_doi(ids[0])[0]
    # # for abstract in abstracts:
    # #     print(abstract)
    # #     print('POTATOE')
    # print(reranking(user_query, abstracts))
