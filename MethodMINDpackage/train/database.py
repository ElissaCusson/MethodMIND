from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
from pymilvus import MilvusClient # Import MilvusClient from pymilvus
from MethodMINDpackage.params import *

def create_milvus():

    # Check if the directory exists; if not, create it
    if not os.path.exists(DATA_DIRECTORY):
        os.makedirs(DATA_DIRECTORY)
        print(f"Directory {DATA_DIRECTORY} created.")
    else:
        print(f"Directory {DATA_DIRECTORY} already exists.")
        # Initialize the Milvus client
    client = MilvusClient(uri=f"{DATA_DIRECTORY}/MethodMIND.db")

    # Define schema
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768),
        FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=512),
        FieldSchema(name="doi", dtype=DataType.VARCHAR, max_length=512),
        FieldSchema(name="keywords", dtype=DataType.VARCHAR, max_length=512),
        FieldSchema(name="publication_date", dtype=DataType.VARCHAR, max_length=512)
    ]
    schema = CollectionSchema(fields=fields, auto_id=True)

    # Create collection
    collection_name = "MethodVectors"

    client.drop_collection(collection_name=collection_name)

    if collection_name in client.list_collections():
        print(f"Collection {collection_name} already exists...")

    client.create_collection(collection_name=collection_name, schema=schema)

    print(f"Collection {collection_name} created successfully.")

    # Creting the index
    # Set up the index parameters
    index_params = client.prepare_index_params()

    # Add an index on the vector field.
    index_params.add_index(
        field_name="embedding",
        metric_type="COSINE",
        index_type="HNSW",
        index_name="vector_index",
        params={ "nlist": 128 })

    # Create an index file
    client.create_index(
        collection_name=collection_name,
        index_params=index_params,
        sync=True
        # Whether to wait for index creation to complete before returning. Defaults to True.
        )

    # print("Index vector created successfully.")

    client.flush(collection_name) # Pass collection_name directly as a string
    client.close()
    # print("Milvus client connection closed.")

    return



#TEST
# Call the function
create_milvus()
