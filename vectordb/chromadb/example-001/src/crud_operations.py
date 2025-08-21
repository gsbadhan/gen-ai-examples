import chromadb
import csv
from chromadb.config import Settings
from typing import List, Dict, Any


class ChromaDBCatalogManager:
    def __init__(self):
        """Initialize Chroma client and collection"""
        self.client = chromadb.Client(Settings(allow_reset=True))
        self.client.reset()  # Start fresh
        self.collection = self.client.create_collection(name="products")
        print("ChromaDB 'products' collection initialized")

    def create_catalog_from_csv(self, csv_file_path: str) -> None:
        """
        CREATE: Populate collection from CSV file
        """
        print("\n--- POPULATING CATALOG (CREATE) ---")
        
        documents, metadatas, ids = [], [], []
        
        with open(csv_file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Prepare the document text for embedding
                doc_text = self._create_document_text(row)
                documents.append(doc_text)
                
                # Prepare metadata for filtering
                metadata = self._create_metadata(row)
                metadatas.append(metadata)
                ids.append(row['product_id'])
        
        # Add all products in a single batch operation
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Added {len(ids)} products to catalog")


    def search_products(self, query_text: str, n_results: int = 3, filters: Dict[str, Any] = None) -> List[Dict]:
        """
        READ: Search products with optional filters
        """
        print(f"\n--- SEARCHING PRODUCTS: '{query_text}' ---")
        
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where=filters,
            include=['documents', 'metadatas', 'distances']
        )
        
        formatted_results = []
        for i, (doc, meta, distance) in enumerate(zip(results['documents'][0], 
                                                     results['metadatas'][0], 
                                                     results['distances'][0])):
            result = {
                'rank': i + 1,
                'name': meta['name'],
                'price': meta['price'],
                'in_stock': meta['in_stock'],
                'category': meta['category'],
                'distance': round(distance, 3),
                'snippet': doc[:100] + '...' if len(doc) > 100 else doc
            }
            formatted_results.append(result)
            print(f"{i+1}. {meta['name']} (${meta['price']}, {meta['category']}) - Distance: {distance:.3f}")
        
        return formatted_results


    def update_product(self, product_id: str, new_price: float = None, 
                      in_stock: bool = None, new_description: str = None) -> bool:
        """
        UPDATE: Modify product information
        """
        print(f"\n--- UPDATING PRODUCT {product_id} ---")
        
        # Get existing product data
        existing_data = self.collection.get(ids=[product_id])
        if not existing_data['ids']:
            print(f"Product {product_id} not found")
            return False
        
        # Prepare updated data
        current_meta = existing_data['metadatas'][0]
        updated_metadata = current_meta.copy()
        
        # Update fields if provided
        if new_price is not None:
            updated_metadata["price"] = new_price
        if in_stock is not None:
            updated_metadata["in_stock"] = in_stock
        
        # Update document text if description changed
        current_doc = existing_data['documents'][0]
        if new_description:
            updated_document = new_description
        else:
            # Keep the document structure but reflect price/stock changes
            updated_document = current_doc  # In a real scenario, you might rebuild this
        
        # Perform the update
        self.collection.update(
            ids=[product_id],
            documents=[updated_document],
            metadatas=[updated_metadata]
        )
        
        print(f"Updated product {product_id}")
        print(f"New Price: ${updated_metadata.get('price')}")
        print(f"In Stock: {updated_metadata.get('in_stock')}")
        return True

    def delete_product(self, product_id: str) -> bool:
        """
        DELETE: Remove a product from catalog
        """
        print(f"\n--- DELETING PRODUCT {product_id} ---")
        
        # Check if product exists first
        existing_data = self.collection.get(ids=[product_id])
        if not existing_data['ids']:
            print(f"Product {product_id} not found")
            return False
        
        self.collection.delete(ids=[product_id])
        print(f"Deleted product {product_id}")
        return True

    def get_product_count(self) -> int:
        """Get total number of products in collection"""
        return self.collection.count()

    def _create_document_text(self, product_data: Dict) -> str:
        """Helper method to create document text for embedding"""
        return f"{product_data['name']}. {product_data['description']} " \
               f"Category: {product_data['category']}. Price: ${product_data['price']}."

    def _create_metadata(self, product_data: Dict) -> Dict:
        """Helper method to create metadata object"""
        return {
            "product_id": product_data['product_id'],
            "category": product_data['category'],
            "price": float(product_data['price']),
            "in_stock": product_data['in_stock'] == 'True',
            "name": product_data['name']
        }




if __name__ == "__main__":
    # Initialize catalog manager
    catalog_mgr = ChromaDBCatalogManager()
    
    # 1. CREATE - Populate catalog from CSV
    catalog_mgr.create_catalog_from_csv('data/product_catalog.csv')
    
    # 2. READ - Search examples
    # Semantic search
    catalog_mgr.search_products("comfortable headphones for running", n_results=3)
    
    # Filtered search
    laptop_filters = {"$and": [{"category": {"$eq": "Laptop"}}, {"price": {"$lte": 1000.0}}]}
    catalog_mgr.search_products("powerful laptop", n_results=5, filters=laptop_filters)
    
    # 3. UPDATE - Modify a product
    catalog_mgr.update_product(
        product_id="prod_042",
        new_price=49.99,
        in_stock=False,
        new_description="Apple Laptop Space Gray. A high-quality space gray laptop by Apple. This product is currently on backorder. New low price!"
    )
    
    # 4. DELETE - Remove a product
    catalog_mgr.delete_product("prod_100")
    
    # 5. Verify final state
    final_count = catalog_mgr.get_product_count()
    print(f"\nFinal number of products in catalog: {final_count}")