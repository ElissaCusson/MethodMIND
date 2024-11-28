import google.generativeai as genai
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from transformers import AutoModel, AutoTokenizer
import google.generativeai as genai
import torch
from MethodMINDpackage.params import GEMINI_API_KEY, DATABASE_PATH
from langchain_milvus import Milvus


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

    # Return the list of embeddings
    return user_input_embeddings

# Test
user_query = "Which methods can I use to measure tremor decrease and gait improvement in Parkinson patients receiving deep brain stimulation?"
embedded_query = user_input_enhancing(user_query)

if isinstance(embedded_query, str):
    # Handle error message
    print(embedded_query)
else:
    # Process embeddings
    print(f"Generated {len(embedded_query)} embeddings.")


def search_similarity(query, k=3):
    vectorstore = Milvus(
        connection_args={
            "uri": DATABASE_PATH,  # Path to the Milvus database (or connection details)
        }
    )
    results = vectorstore.similarity_search(query, k=k)
    return results

# Display the most similar document
similarity = search_similarity(embedded_query)
print("Most similar document:", similarity[0]['text'])
