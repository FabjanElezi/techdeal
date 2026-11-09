from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase

from .models import Category, Contact, Product


class ShopTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_catalog', verbosity=0)
        cls.p1, cls.p2 = Product.objects.all()[:2]

    def test_pages_load(self):
        paths = ['/', '/about/', '/services/', '/faq/', '/contact/', '/cart/', '/login/', '/register/']
        paths += [f'/category/{c.pk}/' for c in Category.objects.all()]
        paths += [f'/product/{p.pk}/' for p in Product.objects.all()]
        for path in paths:
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 200)

    def test_unknown_ids_are_404(self):
        self.assertEqual(self.client.get('/product/9999/').status_code, 404)
        self.assertEqual(self.client.get('/category/9999/').status_code, 404)

    def test_cart_changes_need_post(self):
        self.assertEqual(self.client.get(f'/cart/add/{self.p1.pk}/').status_code, 405)

    def test_cart_flow(self):
        self.client.post(f'/cart/add/{self.p1.pk}/')
        self.client.post(f'/cart/add/{self.p1.pk}/')
        self.client.post(f'/cart/add/{self.p2.pk}/')
        r = self.client.get('/cart/')
        self.assertEqual(r.context['cart_count'], 3)
        self.assertEqual(r.context['total'], self.p1.price * 2 + self.p2.price)

        self.client.post(f'/cart/update/{self.p1.pk}/', {'quantity': 1})
        self.client.post(f'/cart/remove/{self.p2.pk}/')
        r = self.client.get('/cart/')
        self.assertEqual(r.context['cart_count'], 1)
        self.assertEqual(r.context['total'], self.p1.price)

        r = self.client.post('/checkout/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.client.get('/cart/').context['cart_count'], 0)

    def test_each_visitor_has_own_cart(self):
        self.client.post(f'/cart/add/{self.p1.pk}/')
        other = self.client_class()
        self.assertEqual(other.get('/cart/').context['cart_count'], 0)

    def test_contact_form_validates_and_saves(self):
        r = self.client.post('/contact/', {'name': '', 'email': 'not-an-email', 'message': ''})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Contact.objects.count(), 0)
        r = self.client.post('/contact/', {'name': 'Ana', 'email': 'ana@example.com', 'message': 'Hi'})
        self.assertRedirects(r, '/contact/')
        self.assertEqual(Contact.objects.count(), 1)

    def test_register_login_logout(self):
        r = self.client.post('/register/', {
            'username': 'ana', 'email': 'ana@example.com',
            'password1': 'Str0ng-pass-123', 'password2': 'Str0ng-pass-123',
        })
        self.assertRedirects(r, '/')
        user = User.objects.get(username='ana')
        self.assertTrue(user.password.startswith('pbkdf2_'), 'password must be hashed')
        self.assertTrue(self.client.get('/').context['user'].is_authenticated)

        self.client.post('/logout/')
        self.assertFalse(self.client.get('/').context['user'].is_authenticated)

        r = self.client.post('/login/', {'username': 'ana', 'password': 'wrong'})
        self.assertEqual(r.status_code, 200)
        r = self.client.post('/login/', {'username': 'ana', 'password': 'Str0ng-pass-123'})
        self.assertRedirects(r, '/')

    def test_seed_is_idempotent(self):
        call_command('seed_catalog', verbosity=0)
        self.assertEqual(Product.objects.count(), 24)
        self.assertEqual(Product.objects.get(name='iPhone 16').price, Decimal('699'))


class SeedSyncTests(TestCase):
    def test_existing_products_get_new_image_paths(self):
        call_command('seed_catalog', verbosity=0)
        p = Product.objects.get(name='AirPods Max')
        p.image = 'item/old-name.jpg'
        p.save()
        call_command('seed_catalog', verbosity=0)
        p.refresh_from_db()
        self.assertEqual(p.image.name, 'item/AirPods-Max-black.png')
        self.assertEqual(Product.objects.count(), 24)
