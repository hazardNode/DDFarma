# cart.py
from decimal import Decimal

class Cart:
    def __init__(self, request):
        """
        Initialize the cart.
        """
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            # Save an empty cart in the session
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        """
        Add a product to the cart or update its quantity.
        """
        product_id = str(product.id)

        # Get image URL - direct approach
        image_url = None
        try:
            # First try to get a primary image
            primary_image = None
            if hasattr(product, 'images'):
                primary_image = product.images.filter(is_primary=True).first()

            if primary_image and hasattr(primary_image, 'image') and primary_image.image:
                image_url = primary_image.image.url
            else:
                # Try to get the first image
                first_image = None
                if hasattr(product, 'images'):
                    first_image = product.images.first()

                if first_image and hasattr(first_image, 'image') and first_image.image:
                    image_url = first_image.image.url
                # Fall back to old image field
                elif hasattr(product, 'image') and product.image:
                    image_url = product.image.url
        except Exception as e:
            print(f"Error getting product image: {e}")
            image_url = None

        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.price),
                'name': product.name,
                'image_url': image_url
            }
        elif image_url and 'image_url' not in self.cart[product_id]:
            # Update existing cart items with image if missing
            self.cart[product_id]['image_url'] = image_url

        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        # Mark the session as "modified" to make sure it gets saved
        self.session.modified = True

    def remove(self, product):
        """
        Remove a product from the cart.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """
        Iterate over the items in the cart and get the products from the database.
        """
        product_ids = self.cart.keys()
        # Get the product objects and add them to the cart
        from .models import Product

        # Use prefetch_related to load related images efficiently
        products = Product.objects.filter(id__in=product_ids).prefetch_related('images')

        cart = self.cart.copy()

        for product in products:
            cart[str(product.id)]['product'] = product

        for item in cart.values():
            item['price'] = float(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """
        Count all items in the cart.
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """Calculate total price using Decimal for precision."""
        return sum(Decimal(str(item['price'])) * item['quantity'] for item in self.cart.values())

    def clear(self):
        # Remove cart from session
        del self.session['cart']
        self.save()

    # Update your Cart class in cart.py to convert Decimal to float for JSON
    # The get_cart_data method should be updated as follows:

    def get_cart_data(self):
        """Return cart data in a format suitable for AJAX responses, converting Decimal to float for JSON."""
        from .models import Product
        from decimal import Decimal

        product_ids = self.cart.keys()
        # Load products with related images
        products = Product.objects.filter(id__in=product_ids).prefetch_related('images')
        products_dict = {str(p.id): p for p in products}

        items = []
        for key, item in self.cart.items():
            product = products_dict.get(key)
            if product:
                # Get primary image URL safely
                primary_image_url = None
                try:
                    primary_image = product.primary_image
                    if primary_image and hasattr(primary_image, 'url'):
                        primary_image_url = primary_image.url
                except (AttributeError, ValueError):
                    pass

                # Use Decimal for calculations but convert to float for JSON
                price = Decimal(str(item['price']))
                quantity = item['quantity']
                total_price = price * quantity

                items.append({
                    'id': product.id,
                    'name': product.name,
                    'price': float(price),  # Convert to float for JSON
                    'quantity': quantity,
                    'total_price': float(total_price),  # Convert to float for JSON
                    'image': primary_image_url,
                    'stock': product.stock_quantity
                })

        return {
            'items': items,
            'total_price': float(self.get_total_price()),  # Convert to float for JSON
            'total_items': len(self)
        }