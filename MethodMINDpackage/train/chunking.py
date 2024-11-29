from PubMed import get_pubmed_data
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

def chunking(df = None, chunk_size=100, chunk_overlap=20):
    """Splits the abstracts into chunks. The function will return a list of chunks inside a list of abstracts."""
    if df is None:
        df = get_pubmed_data()

    # Filter out rows where Abstract is None or empty
    df = df[df['Abstract'].notna() & (df['Abstract'].str.strip() != '')]


    abstracts_list = df['Abstract'].to_list()
    abstracts_chunks = []

    # Iterate through each abstract and corresponding metadata
    for i, abstract in enumerate(abstracts_list):
        # Get metadata from the DataFrame
        title = df.iloc[i]['Title']
        doi = df.iloc[i]['DOI']
        keywords = df.iloc[i]['Keywords']
        publication_date = df.iloc[i]['Publication Date']
        full_text_link = df.iloc[i]['Full Text Link']

        # Create metadata dictionary
        metadata = {
            'Title': title,
            'DOI': doi,
            'Keywords': keywords,
            'Publication Date': publication_date,
            'Full Text Link': full_text_link
        }

        # Wrap the abstract in a Document object with the metadata
        document = Document(page_content=abstract, metadata=metadata)

        # Create a RecursiveCharacterTextSplitter instance
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

        # Split the document into chunks
        chunks = text_splitter.split_documents([document])

        # Handle short abstracts explicitly
        if not chunks:
            print(f"Warning: Abstract '{title}' (DOI: {doi}) is too short to be chunked. Using the full abstract.")
            chunks = [Document(page_content=abstract, metadata=metadata)]

        # Append the chunks to the list
        abstracts_chunks.append(chunks)

    return abstracts_chunks

# Test
print(chunking(df=get_pubmed_data(), chunk_size=100, chunk_overlap=20))
