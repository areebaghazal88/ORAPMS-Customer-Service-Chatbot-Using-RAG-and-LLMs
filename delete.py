from qdrant_client import QdrantClient

# Connect to your Qdrant instance
client = QdrantClient(host="localhost", port=6333)

# Get all existing collections
collections = client.get_collections().collections

# Delete each collection
for collection in collections:
    print(f"🗑️ Deleting collection: {collection.name}")
    client.delete_collection(collection.name)

print("✅ All collections deleted.")
