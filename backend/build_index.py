import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from sklearn.cluster import MiniBatchKMeans

def build_faiss_index(presets):
    # Load the sentence transformer model
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Convert presets to embeddings
    embeddings = model.encode(presets, show_progress_bar=True)

    # Efficient clustering using MiniBatchKMeans
    n_clusters = 50  # Adjust as needed for your specific case
    kmeans = MiniBatchKMeans(n_clusters=n_clusters, batch_size=100)
    kmeans.fit(embeddings)

    # Create a FAISS index
    index = faiss.IndexFlatL2(embeddings.shape[1])
    faiss_index = faiss.IndexIVFFlat(index, embeddings.shape[1], n_clusters, faiss.METRIC_L2)
    faiss_index.train(embeddings)  # Train the index on the embeddings
    faiss_index.add(embeddings)     # Add embeddings to the index

    return faiss_index

if __name__ == "__main__":
    # Example: Load your presets here (this should be replaced with actual loading logic)
    presets = ["preset1", "preset2", "preset3"]  # Replace with actual presets
    
    # Build the index
    faiss_index = build_faiss_index(presets)

    # Save the FAISS index to a file (optional)
    faiss.write_index(faiss_index, "faiss_index.bin")
