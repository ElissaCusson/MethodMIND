import google.generativeai as genai
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from transformers import AutoModel, AutoTokenizer
import google.generativeai as genai
import torch
from MethodMINDpackage.params import GEMINI_API_KEY

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
embeddings = user_input_enhancing(user_query)

if isinstance(embeddings, str):
    # Handle error message
    print(embeddings)
else:
    # Process embeddings
    print(f"Generated {len(embeddings)} embeddings.")
