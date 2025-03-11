# E-Commerce API Documentation

This document provides a comprehensive guide to the e-commerce API endpoints, organized by user roles and functionality.

## Table of Contents
- [Base URL](#base-url)
- [Authentication](#authentication)
- [User Account Operations](#user-account-operations)
- [Customer Operations](#customer-operations)
- [Store Owner Operations](#store-owner-operations)
- [Admin Operations](#admin-operations)
- [Helper Commands](#helper-commands)

## Base URL

```
http://localhost:8000/api
```

## Authentication

### Login Endpoints

| Method | Endpoint | Description | User Role |
|--------|----------|-------------|-----------|
| POST | `/token/` | Login as Customer | Customer |
| POST | `/token/` | Login as Store Owner | Store Owner |
| POST | `/token/` | Login as Admin | Admin |
| POST | `/logout/` | Logout (Requires refresh token) | Any |

### Authentication Example

```json
// Login Request
POST /api/token/
{
  "username": "john_doe",
  "password": "password123"
}

// Logout Request
POST /api/logout/
Authorization: Bearer {{token}}
{
  "refresh": "your_refresh_token_here"
}
```

## User Account Operations

| Method | Endpoint | Description | Required Role |
|--------|----------|-------------|--------------|
| POST | `/accounts/users/` | Create New User Account | None |
| GET | `/accounts/users/me/` | Get My Account Information | Any |
| PATCH | `/accounts/users/me/` | Update My Profile | Any |
| POST | `/accounts/users/change_password/` | Change Password | Any |
| GET | `/accounts/users` | Get All Users | Admin |
| DELETE | `/accounts/users/{id}/` | Delete User Account | Admin |

### User Account Examples

```json
// Create User
POST /api/accounts/users/
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "testpassword123",
  "phone_number": "1234567890",
  "address": "123 Test St",
  "profile_picture": null,
  "role": "customer"
}

// Update Profile
PATCH /api/accounts/users/me/
Authorization: Bearer {{token}}
{
  "first_name": "sa",
  "last_name": "ika",
  "email": "testuser@testuser.com",
  "phone_number": "0987654321",
  "address": "456 Updated St"
}
```

## Customer Operations

| Method | Endpoint | Description | Required Role |
|--------|----------|-------------|--------------|
| GET | `/products/{id}/` | Get Product by ID | Any |
| POST | `/products/{id}/add_review/` | Add Product Review | Customer |
| POST | `/cart/` | Add Product to Cart | Customer |
| PUT | `/cart/{id}/` | Update Cart Item Quantity | Customer |
| GET | `/cart/` | Get Cart Contents | Customer |
| DELETE | `/cart/{id}/` | Remove Item from Cart | Customer |
| POST | `/orders/` | Create Order from Cart | Customer |
| POST | `/orders/` | Create Direct Order | Customer |
| GET | `/orders/` | Get My Orders | Customer |

### Cart and Order Examples

```json
// Add to Cart
POST /api/cart/
Authorization: Bearer {{token}}
{
  "product": 1,
  "quantity": 2
}

// Create Order from Cart
POST /api/orders/
Authorization: Bearer {{token}}
{
  "from_cart": true
}

// Create Direct Order
POST /api/orders/
Authorization: Bearer {{token}}
{
  "product_id": 12,
  "quantity": 2
}
```

## Store Owner Operations

| Method | Endpoint | Description | Required Role |
|--------|----------|-------------|--------------|
| GET | `/stores/` | Get My Stores | Store Owner |
| POST | `/stores/` | Create New Store | Store Owner |
| GET | `/stores/{id}/` | Get Specific Store | Store Owner |
| PUT | `/stores/{id}/` | Update Store | Store Owner |
| DELETE | `/stores/{id}/` | Delete Store | Store Owner |
| POST | `/products/` | Create Product | Store Owner |
| PUT | `/products/{id}/` | Update Product | Store Owner |
| GET | `/products/{id}/` | Get Product Details | Any |
| DELETE | `/products/{id}/` | Delete Product | Store Owner |
| GET | `/products/my_products` | Get My Products | Store Owner |
| GET | `/orders` | Get Store Orders | Store Owner |
| PATCH | `/orders/{id}/update_status/` | Update Order Status | Store Owner |

### Store Owner Examples

```json
// Create Store
POST /api/stores/
Authorization: Bearer {{token}}
{
  "name": "Test Store",
  "address": "123 Main St",
  "location": "City",
  "category_ids": [1, 3, 2, 5]
}

// Create Product
POST /api/products/
Authorization: Bearer {{token}}
{
  "name": "New Product",
  "description": "Product description",
  "price": 9.99,
  "stock": 1,
  "brand_id": 2,
  "category_ids": [3, 2],
  "store_id": 4
}
```

## Admin Operations

| Method | Endpoint | Description | Required Role |
|--------|----------|-------------|--------------|
| GET | `/products/` | Get All Products | Admin |
| GET | `/products/?page_size=all` | Get Products with Pagination | Any |
| GET | `/stores/` | Get All Stores | Admin |
| POST | `/products/` | Create Product (Admin) | Admin |
| PUT | `/products/{id}/` | Update Product (Admin) | Admin |
| POST | `/stores/` | Create Store (Admin) | Admin |
| PATCH | `/stores/{id}/` | Update Store (Admin) | Admin |
| POST | `/brands/` | Create Brand | Admin |
| POST | `/categories/` | Create Category | Admin |
| GET | `/stores/storeCategory` | Get Store Categories | Admin |
| POST | `/stores/storeCategory` | Create Store Category | Admin |
| PUT | `/stores/storeCategory/{id}/` | Update Store Category | Admin |
| DELETE | `/stores/storeCategory/{id}/` | Delete Store Category | Admin |
| PATCH | `/orders/{id}/update_status/` | Update Order Status (Admin) | Admin |

### Admin Examples

```json
// Create Category
POST /api/categories/
Authorization: Bearer {{token}}
{
  "name": "admin categories"
}

// Update Order Status
PATCH /api/orders/{id}/update_status/
Authorization: Bearer {{token}}
{
  "status": "Cancelled"
}
```

## Helper Commands

Database reset commands:
```bash
# Remove database
rm db.sqlite3

# Clean migrations
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

# Recreate migrations and database
djmm  # makemigrations
djm   # migrate
py manage.py populate_db
djs   # runserver
```

## Authentication Flow

1. Register a new user account (if needed)
2. Login with username and password to get access token
3. Include the access token in the Authorization header for authenticated requests:
   `Authorization: Bearer {your_access_token}`

## Common Status Codes

- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Server Error
