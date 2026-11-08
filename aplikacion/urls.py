from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('category/<int:id>/', views.category, name='category'),
    path('product/<int:pk>/', views.product_detail, name='product'),
    path('about/', views.about_view, name='about'),
    path('services/', views.services_view, name='services'),
    path('faq/', views.faq_view, name='faq'),
    path('contact/', views.contact_view, name='contact'),

    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:pk>/', views.cart_add, name='cart_add'),
    path('cart/update/<int:pk>/', views.cart_update, name='cart_update'),
    path('cart/remove/<int:pk>/', views.cart_remove, name='cart_remove'),
    path('checkout/', views.checkout, name='checkout'),

    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # Old addresses from the first version.
    path('shop/', RedirectView.as_view(pattern_name='cart', permanent=True)),
    path('category/<int:id>', RedirectView.as_view(pattern_name='category', permanent=True)),
]
