"""WSGI entry point (also used by Vercel's Python runtime)."""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

application = get_wsgi_application()

# Serverless hosts have no deploy hook, so a new instance makes sure the
# database schema and the demo catalogue exist before serving. Both steps
# are idempotent and take well under a second once done.
if os.environ.get('VERCEL') and os.environ.get('DATABASE_URL'):
    import logging

    from django.core.management import call_command

    try:
        call_command('migrate', interactive=False, verbosity=0)
        call_command('seed_catalog', verbosity=0)
    except Exception:  # e.g. two cold starts migrating at once; the other one wins
        logging.getLogger(__name__).exception('startup migrate/seed failed')

app = application
