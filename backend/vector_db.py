import chromadb

# start chromadb
client = chromadb.PersistentClient(path="./chroma_db")

# create the table
collection = client.get_or_create_collection(name="knowledge_base")

# add documents to the table
def add_document(doc_id, text, metadata=None):
    collection.add(
        ids=[doc_id],
        documents=[text],
        metadatas=[metadata or {}]
    )
# search documents in the table
def search_document(query_text, n_results=3):
    results = collection.query(
        query_texts=[query_text],
        n_results=n_results
    )
    return results
