# ShopZone Backend

ShopZone Backend is a Django REST Framework e-commerce API for products, stores, carts, orders, reviews, and JWT authentication. It also includes Stripe payment-intent endpoints, OpenAPI docs, and a seeded demo dataset for local development.

## Tech Stack

- Django
- Django REST Framework
- SimpleJWT
- django-filter
- drf-spectacular
- Stripe
- SQLite for local development

## Project Highlights

- Role-based access for customers, store owners, and admins.
- Product catalog with brands, categories, store ownership, and reviews.
- Cart and order flows with order status updates.
- Absolute product image URLs in cart and order responses when request context is available.
- Ready-to-run API examples in `API.http`.

## Base URLs

- API root: `http://localhost:8000/api`
- Admin panel: `http://localhost:8000/admin/`
- Swagger UI: `http://localhost:8000/api/docs/swagger/`
- ReDoc: `http://localhost:8000/api/docs/redoc/`
- OpenAPI schema: `http://localhost:8000/api/schema/`

## Setup

1. Create and activate a virtual environment.
2. Install dependencies from `requirements.txt`.
3. Run migrations.
4. Seed the database.
5. Start the development server.

```bash

# Remove database
rm db.sqlite3

# Clean migrations
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

# Recreate migrations and database
python manage.py makemigrations
python manage.py migrate
python manage.py populate_db

# runserver
python manage.py runserver
```

## Seed Data

The `populate_db` command creates a realistic demo dataset:

- 20 users across customer, store owner, and admin roles.
- 5 stores.
- 15 brands.
- 15 product categories.
- 19 products.
- 3 reviews per product.
- 5 orders per customer and 2 orders per store owner.
- Cart items for every seeded user.

Default seeded users use the password `password123`.

## Authentication

The API uses JWT authentication.

### Tokens

- `POST /api/token/` - obtain access and refresh tokens.
- `POST /api/token/refresh/` - refresh the access token.
- `POST /logout/` - blacklist the refresh token.

### Login Example

```http
POST /api/token/
Content-Type: application/json

{
  "username": "john_doe",
  "password": "password123"
}
```

### Auth Header

```http
Authorization: Bearer <access-token>
```

## Role Matrix

| Role        | Can Access                                                                    |
| ----------- | ----------------------------------------------------------------------------- |
| Customer    | Own profile, products, reviews, cart, and own orders                          |
| Store Owner | Own stores, own products, and orders containing products from stores they own |
| Admin       | Full access to users, products, brands, categories, stores, and all orders    |

## API Routes

### Accounts

| Method    | Route                                  | Description                 |
| --------- | -------------------------------------- | --------------------------- |
| POST      | `/api/accounts/users/`                 | Create a user account       |
| GET       | `/api/accounts/users/me/`              | Get current user profile    |
| PUT/PATCH | `/api/accounts/users/me/`              | Update current user profile |
| POST      | `/api/accounts/users/change_password/` | Change password             |
| GET       | `/api/accounts/users/`                 | List users                  |
| DELETE    | `/api/accounts/users/{id}/`            | Delete a user               |

### Products

| Method    | Route                            | Description                                    |
| --------- | -------------------------------- | ---------------------------------------------- |
| GET       | `/api/products/`                 | List products                                  |
| POST      | `/api/products/`                 | Create a product                               |
| GET       | `/api/products/{id}/`            | Retrieve a product                             |
| PUT/PATCH | `/api/products/{id}/`            | Update a product                               |
| DELETE    | `/api/products/{id}/`            | Delete a product                               |
| POST      | `/api/products/{id}/add_review/` | Create or update a review                      |
| GET       | `/api/products/{id}/reviews/`    | List reviews for a product                     |
| GET       | `/api/products/my_products/`     | List products owned by the current store owner |
| GET       | `/api/brands/`                   | List brands                                    |
| POST      | `/api/brands/`                   | Create a brand                                 |
| GET       | `/api/categories/`               | List categories                                |
| POST      | `/api/categories/`               | Create a category                              |

### Stores

| Method    | Route                             | Description                            |
| --------- | --------------------------------- | -------------------------------------- |
| GET       | `/api/stores/`                    | List stores visible to the user        |
| POST      | `/api/stores/`                    | Create a store                         |
| GET       | `/api/stores/{id}/`               | Retrieve a store                       |
| PUT/PATCH | `/api/stores/{id}/`               | Update a store                         |
| DELETE    | `/api/stores/{id}/`               | Delete a store                         |
| GET       | `/api/stores/products_all/`       | List products across accessible stores |
| GET       | `/api/stores/storeCategory`       | List store categories                  |
| POST      | `/api/stores/storeCategory`       | Create a store category                |
| GET       | `/api/stores/storeCategory/{id}/` | Retrieve a store category              |
| PUT/PATCH | `/api/stores/storeCategory/{id}/` | Update a store category                |
| DELETE    | `/api/stores/storeCategory/{id}/` | Delete a store category                |

### Cart

| Method    | Route                  | Description                 |
| --------- | ---------------------- | --------------------------- |
| GET       | `/api/cart/`           | Get the current user's cart |
| POST      | `/api/cart/`           | Add a product to the cart   |
| PUT/PATCH | `/api/cart/{item_id}/` | Update cart item quantity   |
| DELETE    | `/api/cart/{item_id}/` | Remove a cart item          |

### Orders

| Method | Route                                | Description                                           |
| ------ | ------------------------------------ | ----------------------------------------------------- |
| GET    | `/api/orders/`                       | List orders visible to the user                       |
| POST   | `/api/orders/`                       | Create an order from a cart or a single product       |
| GET    | `/api/orders/{id}/`                  | Retrieve an order                                     |
| PATCH  | `/api/orders/{id}/update_status/`    | Update order status                                   |
| POST   | `/api/orders/create-payment-intent/` | Create a Stripe payment intent                        |
| POST   | `/api/orders/create_payment_intent/` | Alternate payment intent route exposed by the viewset |

### Documentation

| Method | Route                | Description    |
| ------ | -------------------- | -------------- |
| GET    | `/api/schema/`       | OpenAPI schema |
| GET    | `/api/docs/swagger/` | Swagger UI     |
| GET    | `/api/docs/redoc/`   | ReDoc UI       |

## Common Request Examples

### Add a Product to Cart

```http
POST /api/cart/
Authorization: Bearer <access-token>
Content-Type: application/json

{
  "product": 1,
  "quantity": 2
}
```

### Create an Order from Cart

```http
POST /api/orders/
Authorization: Bearer <access-token>
Content-Type: application/json

{
  "from_cart": true
}
```

### Create a Direct Order

```http
POST /api/orders/
Authorization: Bearer <access-token>
Content-Type: application/json

{
  "product_id": 12,
  "quantity": 2
}
```

### Update Order Status

```http
PATCH /api/orders/{order_id}/update_status/
Authorization: Bearer <access-token>
Content-Type: application/json

{
  "status": "Cancelled"
}
```

## Response Notes

- Product images are stored as text URLs in the `image` field.
- Cart and order responses return `product_image` values derived from the underlying product image.
- If the stored image is a relative path, the API returns an absolute URL when request context is available.

## Useful Commands

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py populate_db
python manage.py runserver
```

## API.http

The `API.http` file contains a ready-to-run collection of authenticated requests for customers, store owners, and admins. It is useful for testing the full API flow from VS Code.

## Notes

- The project uses SQLite by default in local development.
- Stripe secret keys must be configured in the environment before calling payment-intent endpoints.
- Some routes use trailing slashes, so keep them consistent when calling the API.
