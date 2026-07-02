    import random
    rng = random.Random(42)
    CATEGORIES = ["tops","bottoms","shoes","accessories","electronics","home"]
    PRODUCTS = [
        {"id": f"prod_{i:03d}", "name": f"Product {i}", "category": rng.choice(CATEGORIES),
         "price": round(rng.uniform(9.99, 299.99), 2), "in_stock": True}
        for i in range(1, 21)
    ]