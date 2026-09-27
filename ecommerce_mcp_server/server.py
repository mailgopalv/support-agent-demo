"""Private e-commerce MCP server.

This is the 'ecommerce MCP server' for my ecommerce online store
"""

from mcp.server.mcpserver import MCPServer

from data import ORDERS, PRODUCTS

mcp = MCPServer("ecommerce")


@mcp.tool()
def get_order_status(order_id: str) -> str:
    """Get the current delivery status of an order.

    Args:
        order_id: The order id, e.g. "O-5001".
    """
    order = ORDERS.get(order_id)
    if not order:
        return f"No order found with id {order_id}."
    return (
        f"Order {order_id} is currently: {order['status']}. "
        f"Estimated delivery: {order['delivery_estimate']}."
    )

@mcp.tool()
def get_order_details(order_id: str) -> dict:
    """Get full details for an order (product, quantity, dates, status).

    Args:
        order_id: The order id, e.g. "O-5001".
    """
    order = ORDERS.get(order_id)
    if not order:
        return {"error": f"No order found with id {order_id}."}
    return order


@mcp.tool()
def search_products(category: str | None = None, color: str | None = None) -> list[dict]:
    """Search the product catalog, optionally filtering by category and/or color.

    Args:
        category: e.g. "electronics", "outdoor", "kitchen". Optional.
        color: e.g. "blue", "black", "green". Optional.
    """
    results = []
    for product in PRODUCTS.values():
        if category and product["category"].lower() != category.lower():
            continue
        if color and product["color"].lower() != color.lower():
            continue
        results.append(product)
    return results


@mcp.tool()
def get_product_details(product_id: str) -> dict:
    """Get full details for a single product.

    Args:
        product_id: The product id, e.g. "P-1001".
    """
    product = PRODUCTS.get(product_id)
    if not product:
        return {"error": f"No product found with id {product_id}."}
    return product


if __name__ == "__main__":
    mcp.run(transport="stdio")
    #mcp.run(transport="streamable-http", host="127.0.0.1", port=8010)
    