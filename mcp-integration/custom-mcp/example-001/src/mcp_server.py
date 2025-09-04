from mcp.server.fastmcp import FastMCP
import asyncio

# MCP server for product catalog
mcpServer = FastMCP(name="Product catalog MCP server")

# product catalog
product_catalog: dict = {
    "prd_001":{"name":"farmhouse pizza", "category":"pizza", "base_price":150},
    "prd_002":{"name":"vegloaded pizza", "category":"pizza", "base_price":350},
    "prd_003":{"name":"Stuffed garlic bread", "category":"sides", "base_price":130},
    "prd_004":{"name":"Stuffed cheesy garlic bread", "category":"sides", "base_price":160},
}

# product discounts
product_discount: dict = {
    "prd_001":{"name":"daily_discount","rate":"10", "unit":"percentage", "start_date":"", "end_date":""},
    "prd_002":{"name":"buy500_discount","rate":"20", "unit":"price", "start_date":"", "end_date":""},
}


# get product detail
@mcpServer.tool(name="product_detail")
async def get_product_detail(product_id: str) -> dict:
    """ Get product detail by id """
    print(f"request for product_id {product_id}")
    product = product_catalog.get(product_id)
    if not product:
        print(f"product_id not {product_id}")
        return {}
    return product


# discounts for product
@mcpServer.tool(name="discounts")
async def get_discounts_of_product(product_id: str) -> dict:
    """ Get discount detail for a product"""
    print(f"request for product_id {product_id}")
    discount = product_discount.get(product_id)
    if not discount:
        print(f"product_id not {product_id}")
        return {}
    return discount 


# run MCP server
if __name__ == "__main__":
    print(f"MCP server starting..")
    asyncio.run(mcpServer.run())


