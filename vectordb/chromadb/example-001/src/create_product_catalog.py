import csv
import random

# Sample data to generate realistic products
product_categories = ["Laptop", "Smartphone", "Headphones", "T-Shirt", "Running Shoes", "Coffee Mug", "Book", "Skateboard", "Watch", "Water Bottle"]
brands = {"Laptop": ["Apple", "Dell", "HP", "Lenovo"],
          "Smartphone": ["Samsung", "Apple", "Google", "Xiaomi"],
          "Headphones": ["Sony", "Bose", "Sennheiser", "Audio-Technica"],
          "T-Shirt": ["Nike", "Adidas", "Levi's", "Uniqlo"],
          "Running Shoes": ["Nike", "Adidas", "New Balance", "Asics"],
          "Coffee Mug": ["Starbucks", "Yeti", "Contigo", "Generic"],
          "Book": ["Penguin", "HarperCollins", "Random House", "Self-Published"],
          "Skateboard": ["Element", "Plan B", "Santa Cruz", "Generic"],
          "Watch": ["Casio", "Seiko", "Fossil", "Timex"],
          "Water Bottle": ["Nalgene", "Hydro Flask", "CamelBak", "Generic"]}

colors = ["Black", "White", "Red", "Blue", "Green", "Silver", "Space Gray"]

# Generate 100 sample products
products = []
for i in range(1, 101):
    color = random.choice(colors)
    category = random.choice(product_categories)
    brand = random.choice(brands[category])
    name = f"{brand} {category} {random.choice(colors)}"
    description = f"A high-quality {color.lower()} {category.lower()} by {brand}. Perfect for everyday use."
    price = round(random.uniform(10.99, 999.99), 2)
    in_stock = random.choice([True, False])
    
    products.append({
        "product_id": f"prod_{i:03d}",
        "name": name,
        "description": description,
        "category": category,
        "price": price,
        "in_stock": in_stock
    })

# Write to CSV file
keys = products[0].keys()
with open('data/product_catalog.csv', 'w', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, fieldnames=keys)
    dict_writer.writeheader()
    dict_writer.writerows(products)

print("product_catalog.csv generated successfully with 100 products!")