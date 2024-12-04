from MethodMINDpackage.train.database import connectload, disconnect_client
import re


def firewall_all_keywords(text_input):
    # firewall with all the keywords

    # Connecting to database + getting keywords
    client, collection_name = connectload(database_name="MethodMIND", collection_name="MethodVectors")
    key_words = retrieve_all_keywords(client, collection_name)

    # Handling empty text_input case
    if not text_input:  # if the text_input is empty or None
        return False

    # Create a list of individual keywords, ensuring non-empty values
    split_items = [item.strip() for sublist in key_words for item in sublist.split(',') if item.strip()]

    if not split_items:  # If no valid keywords after filtering empty ones
        print("No valid keywords found.")
        return False

    # Construct the regular expression pattern with proper boundaries
    pattern = r'\b(?:' + '|'.join([re.escape(item.lower()) for item in split_items]) + r')\b'

    # Strip leading/trailing spaces from the text_input before matching
    text_input_clean = text_input.strip().lower()

    # Debug: Print the cleaned input text
    print("Cleaned Input Text:", text_input_clean)

    # Perform the regex search
    match = re.search(pattern, text_input_clean)

    # Debug: Check if a match is found
    print("Match found:", match)

    disconnect_client(client, collection_name)

    return bool(match)



#retrieve keywords for firewall, haven't tested it yet
def retrieve_all_keywords(client, collection_name="MethodVectors"):
    """
    Retrieve all unique keywords from the specified collection.

    Args:
        client (MilvusClient): Milvus client connection.
        collection_name (str): Name of the collection to query.

    Returns:
        set: A set of unique keywords.
    """
    try:
        # Query all keywords from the collection
        results = client.query(
            collection_name=collection_name,
            #expr='',  # No filtering, query all records
            output_fields=["keywords"],  # Specify the field to retrieve
            limit = 10000
        )

        # Extract keywords and ensure uniqueness using a set
        keywords = {record.get("keywords") for record in results if record.get("keywords")}
        print(f"Retrieved {len(keywords)} unique keywords.")
        #testing keywords
        return keywords
    except Exception as e:
        print(f"An error occurred during keyword retrieval: {e}")
        return set()

if __name__=='__main__':
    pass
