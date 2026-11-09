# TechDeal – Django electronics shop

A small online shop for phones, laptops, audio and smartwatches, built with
**Python and Django** during my internship at Dominusoft (2025) and cleaned up
for deployment in 2026.

> Demo only: browsing, the cart and checkout work, but no payment is taken and
> nothing is shipped.

## Features

- **Catalogue** – categories, product pages and featured products from the database
- **Cart** – kept in the visitor's session, so every visitor has their own cart;
  add, change quantity, remove, check out
- **Accounts** – register, log in and log out with Django's auth (hashed passwords)
- **Contact form** – validated with a `ModelForm` and stored for the admin
- **Admin** – manage products, prices, categories and messages in `/admin`
- **Responsive** – Bootstrap 5 layout tested from 320 px phones to desktop

## Tech stack

Python 3.12 · Django 5.1 · PostgreSQL (Neon) in production, SQLite locally ·
WhiteNoise · Bootstrap 5 with one custom stylesheet (`static/css/site.css`) · deployed on Vercel

## Project structure

```
project/       settings, URLs, WSGI entry point
aplikacion/    the shop app
  models.py        Category, Product, Contact, About
  cart.py          session cart
  views.py         pages, cart, checkout, accounts
  management/      seed_catalog command (demo products)
  templates/       Django templates
  tests.py         test suite
media/item/    product photos
```

## Run locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_catalog
python manage.py runserver
```

Then open http://127.0.0.1:8000. Optional: `python manage.py createsuperuser`
for the admin.

## Tests

```bash
python manage.py test aplikacion
```

Covers every page, the cart flow, per-visitor carts, checkout, the contact
form and register / login / logout.

## Configuration

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | Postgres connection string (production) |
| `DJANGO_SECRET_KEY` | Signing key; if missing in production it is derived from `DATABASE_URL` |
| `DJANGO_DEBUG` | `1` for debug mode (local default) |
| `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS` | Comma separated, optional |

On Vercel the app runs migrations and seeds the catalogue on a fresh instance
(`project/wsgi.py`), so a new deployment needs only `DATABASE_URL`.
