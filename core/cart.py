# cart.py
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
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.price),
                'name': product.name
            }
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
        products = Product.objects.filter(id__in=product_ids)
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
        return sum(float(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        # Remove cart from session
        del self.session['cart']
        self.save()

    def get_cart_data(self):
        """Return cart data in a format suitable for AJAX responses"""
        from .models import Product

        product_ids = self.cart.keys()
        products = {str(p.id): p for p in Product.objects.filter(id__in=product_ids)}

        items = []
        for key, item in self.cart.items():
            product = products.get(key)
            if product:
                items.append({
                    'id': product.id,
                    'name': product.name,
                    'price': float(item['price']),
                    'quantity': item['quantity'],
                    'total_price': float(item['price']) * item['quantity'],
                    'image': product.image.url if product.image else None,
                    'stock': product.stock_quantity
                })

        return {
            'items': items,
            'total_price': self.get_total_price(),
            'total_items': len(self)
        }