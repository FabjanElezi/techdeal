"""
Shopping cart kept in the visitor's session.

The first version stored cart rows in the database without an owner, so every
visitor shared one cart. A session cart belongs to one browser, needs no
login and no database writes.
"""
from decimal import Decimal

from .models import Product

SESSION_KEY = 'cart'
MAX_QTY = 10


class Cart:
    def __init__(self, request):
        self.session = request.session
        self.items = self.session.get(SESSION_KEY, {})  # {product_id (str): quantity}

    def _save(self):
        self.session[SESSION_KEY] = self.items
        self.session.modified = True

    def add(self, product_id, qty=1):
        key = str(product_id)
        self.items[key] = min(self.items.get(key, 0) + qty, MAX_QTY)
        self._save()

    def set(self, product_id, qty):
        key = str(product_id)
        if qty <= 0:
            self.items.pop(key, None)
        else:
            self.items[key] = min(qty, MAX_QTY)
        self._save()

    def remove(self, product_id):
        self.items.pop(str(product_id), None)
        self._save()

    def clear(self):
        self.items = {}
        self._save()

    def count(self):
        return sum(self.items.values())

    def lines(self):
        """Cart rows with product, quantity and line total, in a stable order."""
        products = Product.objects.filter(pk__in=self.items.keys())
        rows = []
        for product in products:
            qty = self.items.get(str(product.pk), 0)
            rows.append({'product': product, 'quantity': qty, 'total': product.price * qty})
        # Drop ids whose product no longer exists.
        known = {str(p.pk) for p in products}
        if set(self.items) - known:
            self.items = {k: v for k, v in self.items.items() if k in known}
            self._save()
        return rows

    def total(self, lines=None):
        lines = lines if lines is not None else self.lines()
        return sum((line['total'] for line in lines), Decimal('0'))
