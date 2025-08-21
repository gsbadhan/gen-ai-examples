import unittest
import os
import csv
import tempfile
from src.crud_operations import ChromaDBCatalogManager

class TestChromaDBCatalogIntegration(unittest.TestCase):
    """Integration test suite for ChromaDBCatalogManager"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test data before all tests"""
        cls.test_csv_data = [
            {
                'product_id': 'prod_001',
                'name': 'Test Laptop Pro',
                'description': 'A high-performance laptop for testing',
                'category': 'Laptop',
                'price': '1299.99',
                'in_stock': 'True'
            },
            {
                'product_id': 'prod_002', 
                'name': 'Test Smartphone Lite',
                'description': 'An affordable smartphone for testing',
                'category': 'Smartphone',
                'price': '299.99',
                'in_stock': 'True'
            },
            {
                'product_id': 'prod_003',
                'name': 'Test Headphones Premium',
                'description': 'Noise-cancelling headphones for testing',
                'category': 'Headphones',
                'price': '199.99',
                'in_stock': 'False'
            },
            {
                'product_id': 'prod_004',
                'name': 'Gaming Laptop Extreme',
                'description': 'High-end gaming laptop with RGB lighting',
                'category': 'Laptop',
                'price': '2499.99',
                'in_stock': 'True'
            }
        ]
        
        # Create temporary CSV file
        cls.temp_csv_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        with open(cls.temp_csv_file.name, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=cls.test_csv_data[0].keys())
            writer.writeheader()
            writer.writerows(cls.test_csv_data)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests"""
        os.unlink(cls.temp_csv_file.name)
    
    def setUp(self):
        """Set up before each test"""
        self.catalog_mgr = ChromaDBCatalogManager()
    
    def tearDown(self):
        """Clean up after each test"""
        # Reset client to ensure test isolation
        self.catalog_mgr.client.reset()
    
    def test_1_create_catalog_from_csv(self):
        """Test CREATE operation: Populate catalog from CSV"""
        # Act
        self.catalog_mgr.create_catalog_from_csv(self.temp_csv_file.name)
        
        # Assert
        count = self.catalog_mgr.get_product_count()
        self.assertEqual(count, 4, "Should have 4 products after creation")
        
        # Verify specific products were added
        results = self.catalog_mgr.collection.get(ids=['prod_001'])
        self.assertEqual(len(results['ids']), 1)
        self.assertEqual(results['metadatas'][0]['name'], 'Test Laptop Pro')
    
    def test_2_search_products_semantic(self):
        """Test READ operation: Semantic search"""
        # Arrange
        self.catalog_mgr.create_catalog_from_csv(self.temp_csv_file.name)
        
        # Act
        results = self.catalog_mgr.search_products("powerful computer machine", n_results=2)
        
        # Assert
        self.assertEqual(len(results), 2, "Should return 2 results")
        # Should find laptops first due to semantic similarity
        self.assertIn('Laptop', results[0]['category'])
    
    def test_3_search_products_with_filters(self):
        """Test READ operation: Search with metadata filters"""
        # Arrange
        self.catalog_mgr.create_catalog_from_csv(self.temp_csv_file.name)
        
        # Act - Search for affordable laptops
        filters = {
            "$and": [
                {"category": {"$eq": "Laptop"}},
                {"price": {"$lte": 1500.0}}
            ]
        }
        results = self.catalog_mgr.search_products("good laptop", n_results=5, filters=filters)
        
        # Assert
        self.assertEqual(len(results), 1, "Should find only one affordable laptop")
        self.assertEqual(results[0]['name'], 'Test Laptop Pro')
        self.assertLessEqual(results[0]['price'], 1500.0)
    
    def test_4_update_product(self):
        """Test UPDATE operation: Modify product price and stock status"""
        # Arrange
        self.catalog_mgr.create_catalog_from_csv(self.temp_csv_file.name)
        
        # Act
        success = self.catalog_mgr.update_product(
            product_id="prod_003",
            new_price=179.99,
            in_stock=True,
            new_description="Noise-cancelling headphones for testing - NOW ON SALE!"
        )
        
        # Assert
        self.assertTrue(success, "Update should succeed")
        
        # Verify the update
        results = self.catalog_mgr.collection.get(ids=['prod_003'])
        updated_meta = results['metadatas'][0]
        self.assertEqual(updated_meta['price'], 179.99)
        self.assertTrue(updated_meta['in_stock'])
        
        # Verify document was updated
        self.assertIn("NOW ON SALE", results['documents'][0])
    
    def test_5_update_nonexistent_product(self):
        """Test UPDATE operation: Should fail for non-existent product"""
        # Arrange
        self.catalog_mgr.create_catalog_from_csv(self.temp_csv_file.name)
        
        # Act
        success = self.catalog_mgr.update_product(
            product_id="prod_999",
            new_price=99.99
        )
        
        # Assert
        self.assertFalse(success, "Update should fail for non-existent product")
    
    def test_6_delete_product(self):
        """Test DELETE operation: Remove product from catalog"""
        # Arrange
        self.catalog_mgr.create_catalog_from_csv(self.temp_csv_file.name)
        initial_count = self.catalog_mgr.get_product_count()
        
        # Act
        success = self.catalog_mgr.delete_product("prod_002")
        
        # Assert
        self.assertTrue(success, "Delete should succeed")
        final_count = self.catalog_mgr.get_product_count()
        self.assertEqual(final_count, initial_count - 1, "Count should decrease by 1")
        
        # Verify product is gone
        results = self.catalog_mgr.collection.get(ids=['prod_002'])
        self.assertEqual(len(results['ids']), 0, "Product should no longer exist")
    
    def test_7_delete_nonexistent_product(self):
        """Test DELETE operation: Should fail for non-existent product"""
        # Arrange
        self.catalog_mgr.create_catalog_from_csv(self.temp_csv_file.name)
        
        # Act
        success = self.catalog_mgr.delete_product("prod_999")
        
        # Assert
        self.assertFalse(success, "Delete should fail for non-existent product")
    
    def test_8_crud_comprehensive_workflow(self):
        """Test complete CRUD workflow: Create, Read, Update, Delete"""
        # CREATE
        self.catalog_mgr.create_catalog_from_csv(self.temp_csv_file.name)
        self.assertEqual(self.catalog_mgr.get_product_count(), 4)
        
        # READ - Verify initial state
        results = self.catalog_mgr.search_products("test laptop", n_results=1)
        self.assertEqual(results[0]['price'], 1299.99)
        
        # UPDATE
        self.catalog_mgr.update_product("prod_001", new_price=1199.99)
        
        # READ - Verify update
        results = self.catalog_mgr.search_products("test laptop", n_results=1)
        self.assertEqual(results[0]['price'], 1199.99)
        
        # DELETE
        self.catalog_mgr.delete_product("prod_004")
        self.assertEqual(self.catalog_mgr.get_product_count(), 3)
        
        # Final verification
        results = self.catalog_mgr.search_products("gaming", n_results=1)
        self.assertEqual(len(results), 0, "Gaming laptop should be deleted")

if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)