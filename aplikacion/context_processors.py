from .cart import Cart
from .models import Category


def shop(request):
    """Categories for the menu and the cart badge, on every page."""
    return {
        'allCategory': Category.objects.all(),
        'cart_count': Cart(request).count(),
    }
