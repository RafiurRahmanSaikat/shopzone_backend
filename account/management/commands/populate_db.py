# management/commands/populate_db.py
from random import choice, randint, sample

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from order.models import Cart, CartItem, Order, OrderProduct
from product.models import Brand, Category, Product, Review
from store.models import Store, StoreCategory

User = get_user_model()


class Command(BaseCommand):
    help = "Populate the database with real data"

    def handle(self, *args, **kwargs):
        # ---------------------
        # 1. Create Users (20 users)
        # ---------------------
        users_data = [
            {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "username": "john_doe",
                "profile_picture": "https://i.ibb.co.com/qMWG0D1j/user-avatar.png",
            },
            {
                "first_name": "Tommy",
                "last_name": "Smith",
                "email": "tommy.smith@example.com",
                "username": "tommy_smith",
                "profile_picture": "https://i.ibb.co.com/qMWG0D1j/user-avatar.png",
            },
            {
                "first_name": "Alice",
                "last_name": "Johnson",
                "email": "alice.johnson@example.com",
                "username": "alice_johnson",
                "profile_picture": "https://i.ibb.co.com/qMWG0D1j/user-avatar.png",
            },
            {
                "first_name": "Bob",
                "last_name": "Williams",
                "email": "bob.williams@example.com",
                "username": "bob_williams",
                "profile_picture": "https://i.ibb.co.com/qMWG0D1j/user-avatar.png",
            },
            {
                "first_name": "Emma",
                "last_name": "Brown",
                "email": "emma.brown@example.com",
                "username": "emma_brown",
                "profile_picture": "https://i.ibb.co.com/qMWG0D1j/user-avatar.png",
            },
            {
                "first_name": "Sophia",
                "last_name": "Davis",
                "email": "sophia.davis@example.com",
                "username": "sophia_davis",
                "profile_picture": "https://i.ibb.co.com/qMWG0D1j/user-avatar.png",
            },
            {
                "first_name": "James",
                "last_name": "Miller",
                "email": "james.miller@example.com",
                "username": "james_miller",
                "profile_picture": "https://i.ibb.co.com/qMWG0D1j/user-avatar.png",
            },
            {
                "first_name": "Oliver",
                "last_name": "Garcia",
                "email": "oliver.garcia@example.com",
                "username": "oliver_garcia",
                "profile_picture": "https://i.ibb.co.com/qMWG0D1j/user-avatar.png",
            },
            {
                "first_name": "Mia",
                "last_name": "Martinez",
                "email": "mia.martinez@example.com",
                "username": "mia_martinez",
                "profile_picture": "https://i.ibb.co.com/qMWG0D1j/user-avatar.png",
            },
            {
                "first_name": "Liam",
                "last_name": "Rodriguez",
                "email": "liam.rodriguez@example.com",
                "username": "liam_rodriguez",
                "profile_picture": "https://i.ibb.co.com/qMWG0D1j/user-avatar.png",
            },
            {
                "first_name": "Lucas",
                "last_name": "Perez",
                "email": "lucas.perez@example.com",
                "username": "lucas_perez",
                "profile_picture": "https://i.ibb.co.com/qMWG0D1j/user-avatar.png",
            },
            {
                "first_name": "Isabella",
                "last_name": "Hernandez",
                "email": "isabella.hernandez@example.com",
                "username": "isabella_hernandez",
                "profile_picture": "https://i.ibb.co.com/qMWG0D1j/user-avatar.png",
            },
            {
                "first_name": "Amelia",
                "last_name": "Lopez",
                "email": "amelia.lopez@example.com",
                "username": "amelia_lopez",
                "profile_picture": "https://i.ibb.co.com/qMWG0D1j/user-avatar.png",
            },
            {
                "first_name": "Ethan",
                "last_name": "Gonzalez",
                "email": "ethan.gonzalez@example.com",
                "username": "ethan_gonzalez",
                "profile_picture": "https://i.ibb.co.com/qMWG0D1j/user-avatar.png",
            },
            {
                "first_name": "Charlotte",
                "last_name": "Wilson",
                "email": "charlotte.wilson@example.com",
                "username": "charlotte_wilson",
                "profile_picture": "https://i.ibb.co.com/qMWG0D1j/user-avatar.png",
            },
            {
                "first_name": "Aiden",
                "last_name": "Anderson",
                "email": "aiden.anderson@example.com",
                "username": "aiden_anderson",
                "profile_picture": "https://i.ibb.co.com/qMWG0D1j/user-avatar.png",
            },
            {
                "first_name": "Scarlett",
                "last_name": "Thomas",
                "email": "scarlett.thomas@example.com",
                "username": "scarlett_thomas",
                "profile_picture": "https://i.ibb.co.com/qMWG0D1j/user-avatar.png",
            },
            {
                "first_name": "Jackson",
                "last_name": "Taylor",
                "email": "jackson.taylor@example.com",
                "username": "jackson_taylor",
                "profile_picture": "https://i.ibb.co.com/qMWG0D1j/user-avatar.png",
            },
            {
                "first_name": "Victoria",
                "last_name": "Moore",
                "email": "victoria.moore@example.com",
                "username": "victoria_moore",
                "profile_picture": "https://i.ibb.co.com/qMWG0D1j/user-avatar.png",
            },
        ]
        roles = ["customer", "store_owner", "admin"]
        users = []
        for index, user_data in enumerate(users_data):
            user, created = User.objects.get_or_create(
                username=user_data["username"],
                defaults={
                    "first_name": user_data["first_name"],
                    "last_name": user_data["last_name"],
                    "email": user_data["email"],
                    "profile_picture": user_data["profile_picture"],
                    "phone_number": f"555-010{index+1}",
                    "address": f"{index+1} Main St, City, Country",
                    "role": roles[index % len(roles)],
                },
            )
            if created:
                user.set_password("password123")
                user.save()
            users.append(user)
        self.stdout.write(self.style.SUCCESS(f"Created {len(users)} users"))

        # ---------------------
        # 2. Create Store Categories
        # ---------------------
        store_categories = ["Electronics", "Fashion", "Groceries", "Books", "Furniture"]
        store_category_objs = [
            StoreCategory.objects.get_or_create(name=category)[0]
            for category in store_categories
        ]
        self.stdout.write(
            self.style.SUCCESS(f"Created {len(store_category_objs)} store categories")
        )

        # ---------------------
        # 3. Create Stores (exactly 5)
        # ---------------------
        stores = []
        store_owners = [user for user in users if user.role == "store_owner"]
        for index in range(5):
            # Use a store owner (if available) based on index.
            owner = store_owners[index % len(store_owners)] if store_owners else None
            store, created = Store.objects.get_or_create(
                name=f"BestBuy {index+1}",
                defaults={
                    "address": f"{index+1} Shop Ave, City, Country",
                    "location": f"City {index+1}",
                    "owner": owner,
                },
            )
            stores.append(store)

        # Add store categories to each store.
        for store in stores:
            store.store_categories.add(*sample(store_category_objs, k=2))
        self.stdout.write(self.style.SUCCESS(f"Created {len(stores)} stores"))

        # Designate one store as EMPTY (i.e. no products and no orders)
        if stores:
            empty_store = choice(stores)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Designated store '{empty_store.name}' as empty (no products/orders)"
                )
            )
            # Use only the other stores when assigning products.
            eligible_stores = [store for store in stores if store != empty_store]
        else:
            eligible_stores = stores

        # ---------------------
        # 4. Create Brands
        # ---------------------
        brands = ["Apple", "Samsung", "Sony", "LG", "Nike", "Adidas", "Microsoft"]
        brand_objs = [Brand.objects.get_or_create(name=brand)[0] for brand in brands]
        self.stdout.write(self.style.SUCCESS(f"Created {len(brand_objs)} brands"))

        # ---------------------
        # 5. Create Product Categories
        # ---------------------
        product_categories = [
            "Mobile",
            "Laptop",
            "Books",
            "TV",
            "Audio",
            "Shoes",
            "Fashion",
            "Electronics",
            "Gaming",
            "Books",
            "Camera",
            "Tablet",
            "Storage",
            "Appliances",
            "Smart Home",
        ]
        category_objs = [
            Category.objects.get_or_create(name=category)[0]
            for category in product_categories
        ]
        self.stdout.write(
            self.style.SUCCESS(f"Created {len(category_objs)} product categories")
        )

        # ---------------------
        # 6. Create Products (assign only to eligible stores)
        # ---------------------
        products_data = [
            {
                "name": "iPhone 14",
                "description": "Apple's latest smartphone with cutting-edge features.",
                "price": 999.99,
                "image": "https://m.media-amazon.com/images/I/61XO4bORHUL._AC_SX679_.jpg",
                "brand": "Apple",
                "categories": ["Mobile", "Electronics"],
            },
            {
                "name": "Samsung Galaxy S23",
                "description": "Flagship smartphone with an amazing camera and display.",
                "price": 899.99,
                "image": "https://m.media-amazon.com/images/I/71ZoDT7a2wL._AC_SL1500_.jpg",
                "brand": "Samsung",
                "categories": ["Mobile", "Electronics"],
            },
            {
                "name": "Sony WH-1000XM5",
                "description": "Industry-leading noise-canceling headphones.",
                "price": 349.99,
                "image": "https://m.media-amazon.com/images/I/61UvHCDqiHL._AC_UF480,480_SR480,480_.jpg",
                "brand": "Sony",
                "categories": ["Electronics", "Audio"],
            },
            {
                "name": "Nike Air Max 270",
                "description": "Stylish and comfortable sneakers from Nike.",
                "price": 130.00,
                "image": "https://m.media-amazon.com/images/I/51W65QNlTlS._AC_SY575_.jpg",
                "brand": "Nike",
                "categories": ["Shoes", "Fashion"],
            },
            {
                "name": "LG 55-Inch 4K TV",
                "description": "Stunning 4K resolution for your home entertainment.",
                "price": 600.00,
                "image": "https://m.media-amazon.com/images/I/81qrVds8-lL._AC_SL1500_.jpg",
                "brand": "LG",
                "categories": ["TV", "Electronics"],
            },
            {
                "name": "MacBook Pro 16-inch",
                "description": "Apple's powerful laptop for professional use.",
                "price": 2399.99,
                "image": "https://m.media-amazon.com/images/I/41S2OSRfBuL._AC_SL1200_.jpg",
                "brand": "Apple",
                "categories": ["Laptop", "Electronics"],
            },
            {
                "name": "Sony PlayStation 5",
                "description": "Next-gen gaming console with impressive performance.",
                "price": 499.99,
                "image": "https://m.media-amazon.com/images/I/51fM0CKG+HL._SL1500_.jpg",
                "brand": "Sony",
                "categories": ["Electronics", "Gaming"],
            },
            {
                "name": "Kindle Paperwhite",
                "description": "Amazon's e-reader with a high-resolution screen.",
                "price": 129.99,
                "image": "https://m.media-amazon.com/images/I/61MdbBO+SEL._AC_SL1500_.jpg",
                "brand": "Amazon",
                "categories": ["Books", "Electronics"],
            },
            {
                "name": "Adidas Ultraboost 22",
                "description": "High-performance running shoes for comfort and speed.",
                "price": 180.00,
                "image": "https://m.media-amazon.com/images/I/51XkCo5XgmL._AC_SY575_.jpg",
                "brand": "Adidas",
                "categories": ["Shoes", "Fashion"],
            },
            {
                "name": "Dell XPS 13",
                "description": "Compact laptop with a stunning display and powerful performance.",
                "price": 1099.99,
                "image": "https://m.media-amazon.com/images/I/61K5ZGbin3L._AC_SL1280_.jpg",
                "brand": "Dell",
                "categories": ["Laptop", "Electronics"],
            },
            {
                "name": "Samsung QLED 8K TV",
                "description": "Ultra-high-definition television with amazing clarity.",
                "price": 2999.99,
                "image": "https://m.media-amazon.com/images/I/51Q+hNO39kL._AC_SL1080_.jpg",
                "brand": "Samsung",
                "categories": ["TV", "Electronics"],
            },
            {
                "name": "Razer Blade 15",
                "description": "Gaming laptop with top-tier performance.",
                "price": 1799.99,
                "image": "https://m.media-amazon.com/images/I/71kBeFDgCkL._AC_SL1500_.jpg",
                "brand": "Razer",
                "categories": ["Laptop", "Gaming"],
            },
            {
                "name": "Bose QuietComfort 45",
                "description": "Noise-cancelling headphones with premium sound.",
                "price": 329.99,
                "image": "https://m.media-amazon.com/images/I/51iAp-Nq7FL._AC_SL1200_.jpg",
                "brand": "Bose",
                "categories": ["Electronics", "Audio"],
            },
            {
                "name": "Canon EOS 90D",
                "description": "High-resolution DSLR camera for photography enthusiasts.",
                "price": 1199.99,
                "image": "https://m.media-amazon.com/images/I/51VGUKF1QRL._AC_SL1000_.jpg",
                "brand": "Canon",
                "categories": ["Camera", "Electronics"],
            },
            {
                "name": "Nikon D7500",
                "description": "Mid-range DSLR camera for high-quality photos.",
                "price": 849.99,
                "image": "https://m.media-amazon.com/images/I/813X74rfb1L._AC_SL1500_.jpg",
                "brand": "Nikon",
                "categories": ["Camera", "Electronics"],
            },
            {
                "name": "Seagate 1TB External HDD",
                "description": "Portable external hard drive for data storage.",
                "price": 59.99,
                "image": "https://m.media-amazon.com/images/I/81tjLksKixL._AC_SL1500_.jpg",
                "brand": "Seagate",
                "categories": ["Storage", "Electronics"],
            },
            {
                "name": "Samsung Galaxy Tab S8",
                "description": "High-performance tablet with a stunning display.",
                "price": 649.99,
                "image": "https://m.media-amazon.com/images/I/51nvMJJH7aL._AC_SL1500_.jpg",
                "brand": "Samsung",
                "categories": ["Tablet", "Electronics"],
            },
            {
                "name": "Samsung SmartThings F-OT-KIT",
                "description": "Smart home control hub to manage devices.",
                "price": 99.99,
                "image": "https://m.media-amazon.com/images/I/7198RX6VLQL._AC_SL1500_.jpg",
                "brand": "Samsung",
                "categories": ["Smart Home", "Electronics"],
            },
            {
                "name": "Whirlpool Washing Machine",
                "description": "Energy-efficient washing machine for your laundry needs.",
                "price": 499.99,
                "image": "https://m.media-amazon.com/images/I/61m2cCUhdbL._AC_SL1500_.jpg",
                "brand": "Whirlpool",
                "categories": ["Appliances", "Home"],
            },
        ]

        products = []
        for product_data in products_data:
            # Assign to a random eligible store (thus leaving the empty store product‑free)
            store_choice = choice(eligible_stores) if eligible_stores else None
            product = Product.objects.create(
                name=product_data["name"],
                description=product_data["description"],
                price=product_data["price"],
                image=product_data["image"],
                stock=randint(1, 100),
                rating=randint(1, 5),
                brand=choice(brand_objs),
                store=store_choice,
            )
            # Attach matching product categories.
            cats = [
                cat for cat in category_objs if cat.name in product_data["categories"]
            ]
            product.categories.add(*cats)
            products.append(product)
        self.stdout.write(self.style.SUCCESS(f"Created {len(products)} products"))

        # ---------------------
        # 7. Create Reviews: EXACTLY 3 reviews per product (by admin and customer)
        # ---------------------
        reviews = []
        eligible_reviewers = [
            user for user in users if user.role in ["admin", "customer"]
        ]
        for product in products:
            reviewers = (
                sample(eligible_reviewers, 3)
                if len(eligible_reviewers) >= 3
                else eligible_reviewers
            )
            for reviewer in reviewers:
                review = Review.objects.create(
                    product=product,
                    user=reviewer,
                    rating=randint(1, 5),
                    comment=f"Great product! I really like the {product.name}.",
                )
                reviews.append(review)
        self.stdout.write(
            self.style.SUCCESS(f"Created {len(reviews)} reviews (3 per product)")
        )

        # ---------------------
        # 8. Create Orders: 3 orders per customer (each order contains 4 products)
        # ---------------------
        order_statuses = ["Confirmed", "Delivered", "Cancelled"]
        orders = []
        for user in [u for u in users if u.role == "customer"]:
            for _ in range(3):
                status_choice = choice(order_statuses)
                order = Order.objects.create(user=user, status=status_choice)
                if len(products) >= 4:
                    products_sample = sample(products, k=4)
                    for product in products_sample:
                        OrderProduct.objects.create(
                            order=order,
                            product=product,
                            quantity=randint(1, 5),
                        )
                orders.append(order)
        self.stdout.write(
            self.style.SUCCESS(f"Created {len(orders)} orders (3 orders per customer)")
        )

        # ---------------------
        # 9. Create Carts and CartItems for all users
        # ---------------------
        for user in users:
            cart, created = Cart.objects.get_or_create(user=user)
            if products:
                products_sample = sample(products, k=3)
                for product in products_sample:
                    CartItem.objects.create(
                        cart=cart,
                        product=product,
                        quantity=randint(1, 5),
                    )
        self.stdout.write(
            self.style.SUCCESS("Created carts and cart items for all users")
        )

        self.stdout.write(
            self.style.SUCCESS("Database populated with real data successfully!")
        )
