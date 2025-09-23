from sentence_transformers import SentenceTransformer

# Load the model
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Example sentences (replace with your product descriptions)
sentences = [
    "Comfortable and stylish red high top sneakers with white stripes.",
    "Premium black leather wallet with multiple card slots and a secure zip pocket."
]

# Generate embeddings
embeddings = model.encode(sentences)

# Print the embeddings
for i, emb in enumerate(embeddings):
    print(f"Embedding for: {sentences[i]}")
    print(emb)
    print()
