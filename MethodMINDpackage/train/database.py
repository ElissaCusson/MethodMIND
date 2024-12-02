import os
from pymilvus import FieldSchema, CollectionSchema, DataType, MilvusClient, connections
from MethodMINDpackage.params import *
# from pymilvus import Collection


def define_schema():
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768),
        FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=512),
        FieldSchema(name="doi", dtype=DataType.VARCHAR, max_length=512),
        FieldSchema(name="keywords", dtype=DataType.VARCHAR, max_length=512),
        FieldSchema(name="full_text_link", dtype=DataType.VARCHAR, max_length=512),
        FieldSchema(name="publication_date", dtype=DataType.VARCHAR, max_length=512)
    ]
    schema = CollectionSchema(fields=fields, auto_id=True)
    return schema

def create_collection(schema, client, collection_name="MethodVectors"):
    if collection_name in client.list_collections():
        print(f"Collection {collection_name} already exists...")
        return
    else:
        client.create_collection(collection_name=collection_name, schema=schema)

    print(f"Collection {collection_name} created successfully.")

    return collection_name

def create_index(client,collection_name="MethodVectors"):

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
    return

def disconnect_client(client, collection_name="MethodVectors"):

    client.flush(collection_name) # Pass collection_name directly as a string
    client.close()
    print("Milvus client connection closed.")
    return

def disconnect_alias(client_alias="default"):
    connections.disconnect(alias=client_alias)

def checkcollection(client,collection_name="MethodVectors"):
    if collection_name not in client.list_collections():
        print(f"Collection {collection_name} does not exist")
    else:
        print(f"Collection {collection_name} exists")

    client.flush(collection_name)
    return collection_name

def create_milvus(database_name="MethodMIND"):

    # Check if the directory exists; if not, create it
    if not os.path.exists(DATA_DIRECTORY):
        os.makedirs(DATA_DIRECTORY)
        print(f"Directory {DATA_DIRECTORY} created.")
    else:
        print(f"Directory {DATA_DIRECTORY} already exists.")
        # Initialize the Milvus client

    # Define the database file path
    db_path = f"{DATA_DIRECTORY}/{database_name}.db"

    # Check if the database file exists
    if not os.path.exists(db_path):
        print("Database does not exist. Creating new database...")
        client = MilvusClient(uri=db_path)  # Initialize Milvus client
    else:
        print("Database already exists. Skipping creation.")
        return

    # Define schema
    schema=define_schema()

    # Create collection
    collection_name=create_collection(schema, client, "MethodVectors")

    # Creating the index
    create_index(client, collection_name="MethodVectors")


    return client

def connectDB_client(database_name="MethodMIND"):
    db_path = f"{DATA_DIRECTORY}/{database_name}.db"

    # Check if the database file exists
    if not os.path.exists(db_path):
        print("Database does not exist")
        return
    else:
        client = MilvusClient(uri=db_path)
    return client

def connectload(database_name="MethodMIND", collection_name="MethodVectors"):
    client=connectDB_client("MethodMIND")
    checkcollection(client,collection_name)
    return client,collection_name

def connectDB_alias(database_name="MethodMIND"):
    db_path = f"{DATA_DIRECTORY}/{database_name}.db"

    # Check if the database file exists
    if not os.path.exists(db_path):
        print("Database does not exist")
        return
    else:
    #     client = MilvusClient(uri=db_path)
    # return client
        connections.connect(alias="default", uri=f"{db_path}")
    return "default"



if __name__=='__main__':
    pass
    #TEST
    # Call the function
    #client=create_milvus("MethodMIND")
