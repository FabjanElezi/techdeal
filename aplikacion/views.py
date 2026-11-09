from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .cart import Cart
from .forms import ContactForm, RegisterForm
from .models import About, Category, Product


# ── Pages ─────────────────────────────────────────────────────

def home_view(request):
    featured = Product.objects.filter(featured=True).select_related('category')[:6]
    if not featured:
        featured = Product.objects.select_related('category')[:6]
    categories = Category.objects.annotate(n=Count('products')).order_by('id').prefetch_related('products')
    return render(request, 'home.html', {'featured': featured, 'categories': categories})


def category(request, id):
    detailCategory = get_object_or_404(Category, pk=id)
    products = detailCategory.products.all()
    return render(request, 'category.html', {'detailCategory': detailCategory, 'products': products})


def product_detail(request, pk):
    product = get_object_or_404(Product.objects.select_related('category'), pk=pk)
    related = Product.objects.filter(category=product.category).exclude(pk=pk)[:3]
    return render(request, 'product.html', {'product': product, 'related': related})


def about_view(request):
    return render(request, 'about.html', {'about': About.objects.first()})


def services_view(request):
    return render(request, 'services.html')


def faq_view(request):
    return render(request, 'faq.html')


def contact_view(request):
    form = ContactForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Thanks! Your message was sent. (Demo shop: nobody will reply.)')
            return redirect('contact')
        messages.error(request, 'Please check the highlighted fields.')
    return render(request, 'contact.html', {'form': form})


# ── Cart ──────────────────────────────────────────────────────

def cart_view(request):
    cart = Cart(request)
    lines = cart.lines()
    return render(request, 'cart.html', {'lines': lines, 'total': cart.total(lines)})


@require_POST
def cart_add(request, pk):
    product = get_object_or_404(Product, pk=pk)
    Cart(request).add(product.pk)
    messages.success(request, f'{product.name} was added to your cart.')
    return redirect(request.POST.get('next') or 'cart')


@require_POST
def cart_update(request, pk):
    try:
        qty = int(request.POST.get('quantity', 1))
    except ValueError:
        qty = 1
    Cart(request).set(pk, qty)
    return redirect('cart')


@require_POST
def cart_remove(request, pk):
    Cart(request).remove(pk)
    return redirect('cart')


@require_POST
def checkout(request):
    cart = Cart(request)
    lines = cart.lines()
    if not lines:
        return redirect('cart')
    total = cart.total(lines)
    cart.clear()
    # Demo shop: no payment and no stored order, just a confirmation.
    return render(request, 'checkout_done.html', {'lines': lines, 'total': total})


# ── Accounts (Django's own auth: hashed passwords, sessions) ──

def register_view(request):
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f'Welcome, {user.username}! Your account was created.')
        return redirect('home')
    return render(request, 'register.html', {'form': form})


def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        messages.success(request, 'You are logged in.')
        return redirect(request.GET.get('next') or 'home')
    return render(request, 'login.html', {'form': form})


@require_POST
def logout_view(request):
    logout(request)
    messages.info(request, 'You are logged out.')
    return redirect('home')
