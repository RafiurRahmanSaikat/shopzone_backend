"""
API Response Collector
======================
Runs all endpoints, saves everything to one clean JSON file.

Usage:
    pip install requests
    python collect_api_responses.py

Output:
    api_responses.json
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"
OUTPUT_FILE = "api_responses.json"

tokens = {}
refresh_tokens = {}


def login(role: str, username: str, password: str):
    try:
        r = requests.post(
            f"{BASE_URL}/token/",
            json={"username": username, "password": password},
            timeout=10,
        )
        body = r.json()
        tokens[role] = body.get("access")
        refresh_tokens[role] = body.get("refresh")
        return body
    except Exception as e:
        return {"error": str(e)}


def auth(role: str) -> dict:
    return {"Authorization": f"Bearer {tokens[role]}"} if tokens.get(role) else {}


def req(method: str, url: str, headers: dict = None, body: dict = None) -> dict:
    h = {"Content-Type": "application/json"}
    if headers:
        h.update(headers)
    try:
        r = getattr(requests, method)(
            f"{BASE_URL}{url}", headers=h, json=body, timeout=10
        )
        return r.json() if r.content else {}
    except Exception as e:
        return {"error": str(e)}


results = []


def add(section: str, label: str, method: str, url: str, response):
    results.append(
        {
            "_section": section,
            "_label": label,
            "method": method.upper(),
            "endpoint": f"{BASE_URL}{url}",
            "response": response,
        }
    )
    print(f"  [{method.upper()}] {url}")


# ─────────────────────────────────────────────
#  AUTH
# ─────────────────────────────────────────────
print("\n[AUTH]")

r = login("customer", "john_doe", "password123")
add("AUTH", "Login as Customer", "post", "/token/", r)

r = login("store_owner", "lucas_perez", "password123")
add("AUTH", "Login as Store Owner", "post", "/token/", r)

r = login("emma", "emma_brown", "password123")
add("AUTH", "Login as Emma Brown (Store Owner)", "post", "/token/", r)

r = login("admin", "alice_johnson", "password123")
add("AUTH", "Login as Admin", "post", "/token/", r)

r = req(
    "post",
    "/logout/",
    headers=auth("admin"),
    body={"refresh": refresh_tokens.get("admin")},
)
add("AUTH", "Logout", "post", "/logout/", r)
login("admin", "alice_johnson", "password123")  # re-login after logout


# ─────────────────────────────────────────────
#  ACCOUNTS
# ─────────────────────────────────────────────
print("\n[ACCOUNTS]")

r = req(
    "post",
    "/accounts/users/",
    body={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "phone_number": "1234567890",
        "address": "123 Test St",
        "profile_picture": None,
        "role": "customer",
    },
)
add("ACCOUNTS", "Create New User Account", "post", "/accounts/users/", r)
login("test_user", "testuser", "testpassword123")

r = req("get", "/accounts/users/me/", headers=auth("test_user"))
add("ACCOUNTS", "Get My Account Information", "get", "/accounts/users/me/", r)

r = req(
    "patch",
    "/accounts/users/me/",
    headers=auth("test_user"),
    body={
        "first_name": "sa",
        "last_name": "ika",
        "email": "testuser@testuser.com",
        "phone_number": "0987654321",
        "address": "456 Updated St",
    },
)
add("ACCOUNTS", "Update My Profile", "patch", "/accounts/users/me/", r)

r = req(
    "post",
    "/accounts/users/change_password/",
    headers=auth("customer"),
    body={
        "old_password": "testpassword123",
        "new_password": "testpassword12",
        "confirm_password": "testpassword12",
    },
)
add("ACCOUNTS", "Change Password", "post", "/accounts/users/change_password/", r)

r = req("get", "/accounts/users", headers=auth("admin"))
add("ACCOUNTS", "Admin: Get All Users", "get", "/accounts/users", r)


# ─────────────────────────────────────────────
#  PRODUCTS
# ─────────────────────────────────────────────
print("\n[PRODUCTS]")

r = req("get", "/products/", headers=auth("admin"))
add("PRODUCTS", "Get All Products", "get", "/products/", r)

r = req("get", "/products/?page_size=all")
add("PRODUCTS", "Get Products (no pagination)", "get", "/products/?page_size=all", r)

r = req("get", "/products/2/")
add("PRODUCTS", "Get Product by ID", "get", "/products/2/", r)

r = req(
    "post",
    "/products/20/add_review/",
    headers=auth("customer"),
    body={"rating": 2, "comment": "Excellent product, highly recommended!"},
)
add("PRODUCTS", "Add Product Review", "post", "/products/20/add_review/", r)

r = req("get", "/products/my_products?page=1", headers=auth("store_owner"))
add("PRODUCTS", "Get My Products (Store Owner)", "get", "/products/my_products", r)

r = req(
    "post",
    "/products/",
    headers=auth("store_owner"),
    body={
        "name": "Store Owner Test Product",
        "description": "Test description",
        "price": 9.99,
        "stock": 1,
        "brand_id": 2,
        "category_ids": [3, 2],
        "store_id": 4,
    },
)
add("PRODUCTS", "Create Product (Store Owner)", "post", "/products/", r)
new_product_id = r.get("id")

if new_product_id:
    r2 = req(
        "put",
        f"/products/{new_product_id}/",
        headers=auth("store_owner"),
        body={
            "name": "Updated Product",
            "description": "Updated description",
            "price": 9.99,
            "stock": 1,
            "brand_id": 2,
            "category_ids": [3, 2],
            "store_id": 4,
        },
    )
    add(
        "PRODUCTS",
        "Update Product (Store Owner)",
        "put",
        f"/products/{new_product_id}/",
        r2,
    )

    r3 = req("delete", f"/products/{new_product_id}/", headers=auth("store_owner"))
    add(
        "PRODUCTS",
        "Delete Product (Store Owner)",
        "delete",
        f"/products/{new_product_id}/",
        r3,
    )

r = req(
    "post",
    "/products/",
    headers=auth("admin"),
    body={
        "name": "Admin Test Product",
        "description": "Admin description",
        "price": 9.99,
        "stock": 1,
        "brand_id": 2,
        "image": None,
        "category_ids": [3, 2],
        "store_id": 2,
    },
)
add("PRODUCTS", "Create Product (Admin)", "post", "/products/", r)
admin_product_id = r.get("id")

if admin_product_id:
    r2 = req(
        "put",
        f"/products/{admin_product_id}/",
        headers=auth("admin"),
        body={
            "name": "Admin Updated Product",
            "description": "Updated",
            "price": 9.25,
            "stock": 1,
            "image": None,
            "brand_id": 3,
            "category_ids": [2],
            "store_id": 2,
        },
    )
    add(
        "PRODUCTS",
        "Update Product (Admin)",
        "put",
        f"/products/{admin_product_id}/",
        r2,
    )


# ─────────────────────────────────────────────
#  CART
# ─────────────────────────────────────────────
print("\n[CART]")

r = req("post", "/cart/", headers=auth("customer"), body={"product": 1, "quantity": 2})
add("CART", "Add Product to Cart", "post", "/cart/", r)
cart_item_id = r.get("id")

r = req("post", "/cart/", headers=auth("customer"), body={"product": 1, "quantity": 1})
add("CART", "Add Same Product Again (Updates Quantity)", "post", "/cart/", r)

r = req("post", "/cart/", headers=auth("customer"), body={"product": 10, "quantity": 1})
add("CART", "Add Different Product to Cart", "post", "/cart/", r)
cart_item_10_id = r.get("id")

if cart_item_id:
    r = req(
        "put", f"/cart/{cart_item_id}/", headers=auth("customer"), body={"quantity": 4}
    )
    add("CART", "Update Cart Item Quantity", "put", f"/cart/{cart_item_id}/", r)

r = req("get", "/cart/", headers=auth("customer"))
add("CART", "Get Cart Contents", "get", "/cart/", r)

if cart_item_10_id:
    r = req("delete", f"/cart/{cart_item_10_id}/", headers=auth("customer"))
    add("CART", "Remove Item from Cart", "delete", f"/cart/{cart_item_10_id}/", r)


# ─────────────────────────────────────────────
#  ORDERS
# ─────────────────────────────────────────────
print("\n[ORDERS]")

r = req("post", "/orders/", headers=auth("customer"), body={"from_cart": True})
add("ORDERS", "Create Order from Cart", "post", "/orders/", r)

r = req(
    "post", "/orders/", headers=auth("customer"), body={"product_id": 12, "quantity": 2}
)
add("ORDERS", "Create Direct Order", "post", "/orders/", r)

r = req("get", "/orders/", headers=auth("customer"))
add("ORDERS", "Get My Orders (Customer)", "get", "/orders/", r)

r = req("get", "/orders", headers=auth("store_owner"))
add("ORDERS", "Get Store Orders (Store Owner)", "get", "/orders", r)

order_id = None
orders_data = r if isinstance(r, list) else r.get("results", [])
if orders_data:
    order_id = orders_data[0].get("id")

if order_id:
    r = req(
        "patch",
        f"/orders/{order_id}/update_status/",
        headers=auth("store_owner"),
        body={"status": "Cancelled"},
    )
    add(
        "ORDERS",
        "Update Order Status (Store Owner)",
        "patch",
        f"/orders/{order_id}/update_status/",
        r,
    )

    r = req(
        "patch",
        f"/orders/{order_id}/update_status/",
        headers=auth("admin"),
        body={"status": "Cancelled"},
    )
    add(
        "ORDERS",
        "Update Order Status (Admin)",
        "patch",
        f"/orders/{order_id}/update_status/",
        r,
    )


# ─────────────────────────────────────────────
#  STORES
# ─────────────────────────────────────────────
print("\n[STORES]")

r = req("get", "/stores/", headers=auth("store_owner"))
add("STORES", "Get My Stores", "get", "/stores/", r)

r = req("get", "/stores/", headers=auth("admin"))
add("STORES", "Get All Stores (Admin)", "get", "/stores/", r)

r = req(
    "post",
    "/stores/",
    headers=auth("store_owner"),
    body={
        "name": "Test Collector Store",
        "address": "123 Main St",
        "location": "Test City",
        "category_ids": [1, 2],
    },
)
add("STORES", "Create New Store", "post", "/stores/", r)
new_store_id = r.get("id")

if new_store_id:
    r2 = req("get", f"/stores/{new_store_id}/", headers=auth("store_owner"))
    add("STORES", "Get Specific Store", "get", f"/stores/{new_store_id}/", r2)

    r2 = req(
        "put",
        f"/stores/{new_store_id}/",
        headers=auth("store_owner"),
        body={
            "name": "Updated Store",
            "address": "456 New Address",
            "location": "New Location",
            "category_ids": [1, 2],
        },
    )
    add("STORES", "Update Store", "put", f"/stores/{new_store_id}/", r2)

    r2 = req("delete", f"/stores/{new_store_id}/", headers=auth("store_owner"))
    add("STORES", "Delete Store", "delete", f"/stores/{new_store_id}/", r2)

r = req(
    "post",
    "/stores/",
    headers=auth("admin"),
    body={
        "name": "Admin Store",
        "address": "456 New Address",
        "location": "New Location",
        "category_ids": [1, 2],
    },
)
add("STORES", "Create Store (Admin)", "post", "/stores/", r)
admin_store_id = r.get("id")

if admin_store_id:
    r2 = req(
        "patch",
        f"/stores/{admin_store_id}/",
        headers=auth("admin"),
        body={
            "name": "Admin Store Updated",
            "address": "456 New Address",
            "location": "New Location",
            "category_ids": [1, 2],
        },
    )
    add("STORES", "Update Store (Admin)", "patch", f"/stores/{admin_store_id}/", r2)


# ─────────────────────────────────────────────
#  BRANDS
# ─────────────────────────────────────────────
print("\n[BRANDS]")

r = req("post", "/brands/", headers=auth("admin"), body={"name": "admin brand"})
add("BRANDS", "Create Brand (Admin)", "post", "/brands/", r)


# ─────────────────────────────────────────────
#  CATEGORIES
# ─────────────────────────────────────────────
print("\n[CATEGORIES]")

r = req(
    "post", "/categories/", headers=auth("admin"), body={"name": "admin categories"}
)
add("CATEGORIES", "Create Category (Admin)", "post", "/categories/", r)


# ─────────────────────────────────────────────
#  STORE CATEGORIES
# ─────────────────────────────────────────────
print("\n[STORE CATEGORIES]")

r = req("get", "/stores/storeCategory", headers=auth("admin"))
add("STORE CATEGORIES", "Get Store Categories", "get", "/stores/storeCategory", r)

r = req("post", "/stores/storeCategory", headers=auth("admin"), body={"name": "Books"})
add("STORE CATEGORIES", "Create Store Category", "post", "/stores/storeCategory", r)
new_cat_id = r.get("id")

if new_cat_id:
    r2 = req(
        "put",
        f"/stores/storeCategory/{new_cat_id}/",
        headers=auth("admin"),
        body={"name": "Updated Category"},
    )
    add(
        "STORE CATEGORIES",
        "Update Store Category",
        "put",
        f"/stores/storeCategory/{new_cat_id}/",
        r2,
    )

    r2 = req("delete", f"/stores/storeCategory/{new_cat_id}/", headers=auth("admin"))
    add(
        "STORE CATEGORIES",
        "Delete Store Category",
        "delete",
        f"/stores/storeCategory/{new_cat_id}/",
        r2,
    )


# ─────────────────────────────────────────────
#  WRITE OUTPUT
# ─────────────────────────────────────────────
print(f"\n── Writing {OUTPUT_FILE} ──")
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"Done! {len(results)} endpoints saved to '{OUTPUT_FILE}'")
