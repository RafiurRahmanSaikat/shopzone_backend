# E-Commerce Backend

This project provides a robust backend for an e-commerce platform. It is built with Django and Django REST Framework and implements endpoints for products, orders, stores, user accounts, and more. The backend supports different user roles such as admin, store owner, and customer with JWT authentication.

## Features

- **Authentication & Authorization:**
  - JWT-based authentication
  - Separate token endpoints for admin, store owner, and customer

- **Products Management:**
  - Create, update, retrieve, and delete products
  - Auto-approval for admin-created products

- **Store Management:**
  - Create and update stores
  - List stores for both admin and store owners
  - Custom endpoints for store-specific operations

- **Orders & Cart:**
  - Create orders from the shopping cart or via direct order creation
  - Update order status (including cancelation) by both store owners and admins

- **Reviews & Ratings:**
  - Customers can add reviews to products

- **Brands & Categories:**
  - Endpoints to create and manage brands and categories

## Technologies

- **Backend Framework:** Django, Django REST Framework
- **Database:** SQLite (default, with an option to use another DB engine)
- **Authentication:** JSON Web Tokens (JWT)
- **Tools:**
  - Postman for API testing
  - Custom management commands for database population

## Getting Started

### Prerequisites

- Python 3.x
- Virtual environment (recommended)
- Dependencies listed in `requirements.txt`

### Installation

1. **Clone the repository:**

   ```bash
   git clone <repository_url>
   cd <repository_directory>

## Reset The Project

2. **Reset and Load Dummy Data:**
   ```bash
   rm db.sqlite3
   find . -path "*/migrations/*.py" -not -name "__init__.py" -exec rm -f {} \;
   find . -type d -name "__pycache__" -exec rm -r {} \;

   python manage.py makemigrations
   python manage.py migrate
   python manage.py populate_db
   python manage.py runserver



