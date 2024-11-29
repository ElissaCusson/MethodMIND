import google.generativeai as genai
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from transformers import AutoModel, AutoTokenizer
import google.generativeai as genai
import torch
from MethodMINDpackage.params import GEMINI_API_KEY, PUBMED_API_KEY
from langchain_milvus import Milvus
from pymilvus import Collection
from MethodMINDpackage.train.database import connectDB_alias, disconnect_alias, connectload, disconnect_client
# from MethodMINDpackage.train.PubMed import get_abstract_by_doi


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
        f"Create a detailed abstract for the following user query:\n\n"
        f"User query: {user_input}\n\n"
        f"Abstract:"
    )

    # Generate the hypothetical abstract
    hypothetical_abstract = llm.generate_content(prompt).text

    # Ensure the hypothetical abstract is valid
    if not hypothetical_abstract or not hypothetical_abstract.strip():
        return "Failed to generate a valid hypothetical abstract."

    # Chunk the hypothetical abstract
    # Create a Document object
    document = Document(page_content=hypothetical_abstract, metadata={"source": "HyDE"})

    # Create a RecursiveCharacterTextSplitter instance
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)

    # Split the document into chunks
    chunks = text_splitter.split_documents([document])


    # Embed the chunks using SciBERT
    # Load SciBERT model and tokenizer
    model_name = "allenai/scibert_scivocab_uncased"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)

    # Prepare the embeddings list
    user_input_embeddings = []

    # Process each chunk
    for chunk in chunks:
        # Tokenize the chunk text
        inputs = tokenizer(chunk.page_content, return_tensors="pt", padding=True, truncation=True, max_length=512)

        # Pass through the model
        with torch.no_grad():
            outputs = model(**inputs)

        # Extract the embeddings (mean pooling over token embeddings)
        chunk_embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
        user_input_embeddings.append(chunk_embedding)
    # print(type(user_input_embeddings[0]))
    # print(user_input_embeddings[0])
    # Return the list of embeddings
    return user_input_embeddings

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


# Test
user_query = "Which methods can I use to measure tremor decrease and gait improvement in Parkinson patients receiving deep brain stimulation?"
embedded_query = user_input_enhancing(user_query)

if isinstance(embedded_query, str):
    # Handle error message
    print(embedded_query)
else:
    # Process embeddings
    print(f"Generated {len(embedded_query)} embeddings.")


# def search_similarity(query, k=3):
#     vectorstore = Milvus(
#         connection_args={
#             "uri": DATABASE_PATH,  # Path to the Milvus database (or connection details)
#         },
#         embedding_function=test_embedding(query)
#     )
#     results = vectorstore.similarity_search(query, k=k)
#     return results

def search_similarity(query, k=3):
    # client=connectDB()
    client_alias = connectDB_alias()

    if client_alias is None:
        print("Failed to connect to the database.")
        return []
    collection = Collection(name="MethodVectors", using=client_alias)

    # Get the query embedding
    query_embedding = test_embedding(query)

    results = collection.search(
        data=[query_embedding],
        anns_field="embedding",
        param={"metric_type": "COSINE", "params": {"nprobe": 10}},  # You can adjust metric_type and nprobe as needed
        limit=k,
        expr=None  # You can add filtering expressions here if needed
    )
    disconnect_alias(client_alias)
    # print(type(results[0][0].id))
    return results[0][0].id

# # Display the most similar document
similarity = search_similarity(user_query, k=1)
# print("Most similar documents:", similarity)

def query_by_id_client(query_id=None):
    """
    Retrieve metadata and vector data for a specific ID from the collection.

    Args:
        client (MilvusClient): Milvus client connection.
        collection_name (str): Name of the collection to query.
        query_id (int): The ID to search for.

    Returns:
        list: Query results containing matched metadata and vector data.
    """
    client,collection_name=connectload()
    if query_id is None:
        print("Query ID is required.")
        disconnect_client(client, collection_name="MethodVectors")
        return

    # Build filter expression for ID
    filter_expression = f"id == {query_id}"

    # Perform query
    try:
        results = client.query(
            collection_name=collection_name,
            expr=filter_expression,  # Filter by ID
            output_fields=["embedding", "title", "doi", "keywords", "full_text_link", "publication_date"]  # Specify fields to retrieve
        )
        print(f"Query completed. Retrieved {len(results)} results.")
        disconnect_client(client, collection_name="MethodVectors")
        return results
    except Exception as e:
        print(f"An error occurred during query: {e}")
        disconnect_client(client, collection_name="MethodVectors")
        return None


from pymilvus import Collection

def query_by_id(user_query, query_id=None):
    """
    Retrieve metadata and vector data for a specific ID from the collection.

    Args:
        query_id (int): The ID to search for.

    Returns:
        list: Query results containing matched metadata and vector data.
    """
    query_id = str(search_similarity(user_query, k=1))
    # Connect and load the collection
    client_alias = connectDB_alias()
    if client_alias is None:
        print("Failed to connect to the database.")
        return []

    collection = Collection(name="MethodVectors", using=client_alias)

    if query_id is None:
        print("Query ID is required.")
        return []

    # Build filter expression for ID
    filter_expression = f"id == {query_id}"

    # Perform the query using Collection.query()
    try:
        results = collection.query(
            expr=filter_expression,  # Filter by ID
            output_fields=["title", "doi", "keywords", "full_text_link", "publication_date"]  # Specify fields to retrieve
        )
        print(f"Query completed. Retrieved {len(results)} results.")
        # print(type(results[0]['doi']))
        return results[0]['doi']
    except Exception as e:
        print(f"An error occurred during query: {e}")
        return None
    finally:
        # Always disconnect after query
        disconnect_alias()




# print(query_by_id(user_query, query_id=None))

# print(get_abstract_by_doi(user_query))
