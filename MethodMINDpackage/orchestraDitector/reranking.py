from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from MethodMINDpackage.orchestraDitector.retrival import *

# Load monoT5
model_name = "castorini/monot5-base-msmarco"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

def reranking(user_input, abstracts, n_results=5):
    # Rerank each document
    ranked_results = []
    for abtract in abstracts:
        input_text = f"Query: {user_input} Document: {abtract}"
        inputs = tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True)
        outputs = model.generate(**inputs)
        relevance_score = tokenizer.decode(outputs[0], skip_special_tokens=True)
        ranked_results.append((abtract, relevance_score))

    # Sort documents by relevance score (e.g., "true" vs. "false")
    ranked_results = sorted(ranked_results, key=lambda x: x[1], reverse=True)

    # Get 5 best abstracts
    results = ranked_results[0:n_results]

    return results


if __name__=="__main__":
    pass
    ########### MVP TEST
    user_query = ''
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

    dois = set(handle_multiple_metadata(ids[0])['doi'])
    print(len(dois))
    # # get_abstract_by_doi tests:
    print(get_abstract_by_doi(dois= [None]))
    print(get_abstract_by_doi(dois= ['10.1007/s00296potatoe-011-2267-2']))
    abstracts = get_abstract_by_doi(dois= dois)[0]
    # for abstract in abstracts:
    #     print(abstract)
    #     print('POTATOE')
    print(reranking(user_query, abstracts))
