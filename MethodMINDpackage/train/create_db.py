from MethodMINDpackage.train.database import create_milvus, disconnect, connectload

if __name__ == "__main__":
    client=create_milvus("MethodMIND")
    disconnect(client, collection_name="MethodVectors")

    client,collection_name=connectload()
    row_count = client.get_collection_stats(collection_name=collection_name)['row_count']
    print(f"Database as {row_count} in collection {collection_name}")
    disconnect(client, collection_name="MethodVectors")