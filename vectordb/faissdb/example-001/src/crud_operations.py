import csv
import faiss
import numpy as np
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD

class FaissCatalogManager:
    def __init__(self, dim: int = 100):
        """
        Initialize FAISS index with TF-IDF embeddings
        """
        self.vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
        self.dim = dim
        self.index = faiss.IndexFlatL2(dim)
        self.documents: Dict[str, str] = {}
        self.metadatas: Dict[str, Dict] = {}
        self.id_to_vector: Dict[str, np.ndarray] = {}
        self.svd = TruncatedSVD(n_components=dim)
        self.is_fitted = False
        print(f"FAISS index initialized with dimension {dim}")

    def create_catalog_from_csv(self, csv_file_path: str) -> None:
        """
        CREATE: Populate FAISS index from CSV file
        """
        print("\n--- POPULATING CATALOG (CREATE) ---")
        texts = []
        rows = []
        
        with open(csv_file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                product_id = row['product_id']
                doc_text = self._create_document_text(row)
                metadata = self._create_metadata(row)
                
                texts.append(doc_text)
                rows.append((product_id, doc_text, metadata))
        
        # Fit TF-IDF
        tfidf_matrix = self.vectorizer.fit_transform(texts)
        
        # Check vocabulary size and adjust SVD if needed
        vocab_size = len(self.vectorizer.get_feature_names_out())
        print(f"Vocabulary size: {vocab_size}")
        
        # RECREATE THE INDEX WITH THE CORRECT DIMENSION
        if vocab_size < self.dim:
            # Use all available features
            actual_dim = vocab_size
            self.svd = TruncatedSVD(n_components=actual_dim)
            print(f"Using all available features: {actual_dim}")
        else:
            actual_dim = self.dim
        
        # RECREATE FAISS INDEX WITH CORRECT DIMENSION
        self.index = faiss.IndexFlatL2(actual_dim)
        self.dim = actual_dim  # Update the dimension
        
        reduced_vectors = self.svd.fit_transform(tfidf_matrix)
        
        # Clear any existing data
        self.documents.clear()
        self.metadatas.clear()
        self.id_to_vector.clear()
        
        # Prepare all vectors for batch addition
        all_vectors = []
        for i, (product_id, doc_text, metadata) in enumerate(rows):
            vector = reduced_vectors[i].astype("float32")
            all_vectors.append(vector)
            
            self.documents[product_id] = doc_text
            self.metadatas[product_id] = metadata
            self.id_to_vector[product_id] = vector
        
        # Add all vectors at once to the index
        if all_vectors:
            self.index.add(np.array(all_vectors))
        
        self.is_fitted = True
        print(f"Added {len(self.documents)} products to FAISS catalog with dimension {self.dim}")


    def search_products(self, query_text: str, n_results: int = 3,
                        filters: Dict[str, Any] = None) -> List[Dict]:
        """
        READ: Search products with optional filters
        """
        if not self.is_fitted:
            raise ValueError("Catalog not initialized. Call create_catalog_from_csv first.")
            
        print(f"\n--- SEARCHING PRODUCTS: '{query_text}' ---")

        # Transform query using fitted vectorizer and SVD
        query_tfidf = self.vectorizer.transform([query_text])
        query_vec = self.svd.transform(query_tfidf)[0].astype("float32")

        distances, indices = self.index.search(np.array([query_vec]), n_results * 5)

        formatted_results = []
        product_ids = list(self.documents.keys())

        for idx, dist in zip(indices[0], distances[0]):
            if idx == -1:
                continue
            product_id = product_ids[idx]
            meta = self.metadatas[product_id]

            if filters and not self._apply_filters(meta, filters):
                continue

            result = {
                'id': product_id,
                'name': meta['name'],
                'price': meta['price'],
                'in_stock': meta['in_stock'],
                'category': meta['category'],
                'distance': round(float(dist), 3),
                'snippet': self.documents[product_id][:100] + "..."
            }
            formatted_results.append(result)

            if len(formatted_results) >= n_results:
                break

        for r in formatted_results:
            print(f"{r['name']} (${r['price']}, {r['category']}) - Distance: {r['distance']:.3f}")

        return formatted_results

    def update_product(self, product_id: str, new_price: float = None,
                       in_stock: bool = None, new_description: str = None) -> bool:
        print(f"\n--- UPDATING PRODUCT {product_id} ---")
        if product_id not in self.documents:
            print(f"Product {product_id} not found")
            return False

        metadata = self.metadatas[product_id]
        if new_price is not None:
            metadata["price"] = new_price
        if in_stock is not None:
            metadata["in_stock"] = in_stock
        if new_description:
            self.documents[product_id] = new_description

        # FIXED: Use TF-IDF transformation instead of model.encode()
        updated_doc = self.documents[product_id]
        updated_tfidf = self.vectorizer.transform([updated_doc])
        new_vector = self.svd.transform(updated_tfidf)[0].astype("float32")

        self.id_to_vector[product_id] = new_vector
        self._rebuild_index()

        print(f"Updated product {product_id} → Price: {metadata['price']}, In Stock: {metadata['in_stock']}")
        return True

    def delete_product(self, product_id: str) -> bool:
        print(f"\n--- DELETING PRODUCT {product_id} ---")
        if product_id not in self.documents:
            print(f"Product {product_id} not found")
            return False

        del self.documents[product_id]
        del self.metadatas[product_id]
        del self.id_to_vector[product_id]
        self._rebuild_index()
        print(f"Deleted product {product_id}")
        return True

    def get_product_count(self) -> int:
        return len(self.documents)

    def _create_document_text(self, product_data: Dict) -> str:
        return f"{product_data['name']}. {product_data['description']} " \
               f"Category: {product_data['category']}. Price: ${product_data['price']}."

    def _create_metadata(self, product_data: Dict) -> Dict:
        return {
            "product_id": product_data['product_id'],
            "category": product_data['category'],
            "price": float(product_data['price']),
            "in_stock": product_data['in_stock'] == 'True',
            "name": product_data['name']
        }

    def _apply_filters(self, metadata: Dict, filters: Dict) -> bool:
        for key, condition in filters.items():
            if isinstance(condition, dict):
                if "$eq" in condition and metadata[key] != condition["$eq"]:
                    return False
                if "$lte" in condition and metadata[key] > condition["$lte"]:
                    return False
            else:
                if metadata[key] != condition:
                    return False
        return True

    def _rebuild_index(self):
        self.index = faiss.IndexFlatL2(self.dim)
        all_vectors = np.array(list(self.id_to_vector.values()), dtype="float32")
        if len(all_vectors) > 0:
            self.index.add(all_vectors)


if __name__ == "__main__":
    catalog_mgr = FaissCatalogManager(dim=100)

    catalog_mgr.create_catalog_from_csv("data/product_catalog.csv")
    catalog_mgr.search_products("comfortable headphones for running", n_results=3)

    laptop_filters = {"category": {"$eq": "Laptop"}, "price": {"$lte": 1000.0}}
    catalog_mgr.search_products("powerful laptop", n_results=5, filters=laptop_filters)

    catalog_mgr.update_product("prod_042", new_price=49.99, in_stock=False,
                               new_description="Apple Laptop Space Gray. High-quality, currently on backorder. New low price!")

    catalog_mgr.delete_product("prod_100")
    print(f"\nFinal number of products: {catalog_mgr.get_product_count()}")