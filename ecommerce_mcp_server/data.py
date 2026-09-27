"""Mock data store standing in for the order and product APIs."""

PRODUCTS = {
    "P-1001": {
        "product_id": "P-1001",
        "name": "Aria Wireless Headphones",
        "category": "electronics",
        "color": "black",
        "price": 79.99,
        "stock": 42,
    },
    "P-1002": {
        "product_id": "P-1002",
        "name": "Aria Wireless Headphones",
        "category": "electronics",
        "color": "blue",
        "price": 79.99,
        "stock": 17,
    },
    "P-1003": {
        "product_id": "P-1003",
        "name": "Trail Runner Backpack",
        "category": "outdoor",
        "color": "green",
        "price": 54.50,
        "stock": 8,
    },
    "P-1004": {
        "product_id": "P-1004",
        "name": "Trail Runner Backpack",
        "category": "outdoor",
        "color": "blue",
        "price": 54.50,
        "stock": 0,
    },
    "P-1005": {
        "product_id": "P-1005",
        "name": "Ceramic Pour-Over Kettle",
        "category": "kitchen",
        "color": "white",
        "price": 32.00,
        "stock": 25,
    },
}

ORDERS = {
    "O-5001": {
        "order_id": "O-5001",
        "customer_email": "jane.doe@example.com",
        "product_id": "P-1001",
        "quantity": 1,
        "status": "packed for delivery",
        "placed_date": "2026-09-10",
        "delivery_estimate": "2026-09-17",
    },
    "O-5002": {
        "order_id": "O-5002",
        "customer_email": "jane.doe@example.com",
        "product_id": "P-1003",
        "quantity": 1,
        "status": "out for delivery",
        "placed_date": "2026-09-08",
        "delivery_estimate": "2026-09-15",
    },
    "O-5003": {
        "order_id": "O-5003",
        "customer_email": "sam.roy@example.com",
        "product_id": "P-1005",
        "quantity": 2,
        "status": "delivered",
        "placed_date": "2026-08-30",
        "delivery_estimate": "2026-09-05",
    },
}
