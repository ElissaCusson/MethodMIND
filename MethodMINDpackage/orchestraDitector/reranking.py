from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Load monoT5
model_name = "castorini/monot5-base-msmarco"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

def reranking(user_input, abstracts, n_results):
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
    results = ranked_results[0:5]

    return results
