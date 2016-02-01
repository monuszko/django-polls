django-poll-app
===============

The solution to https://docs.djangoproject.com/en/dev/intro/tutorial01/

Getting Started
---------------

### Initial Setup ###
1. Make a new virtualenv: ``virtualenv env``
2. Activate the virtualenv: ``source env/bin/activate``
3. Install required packages: ``pip install -r requirements.txt``
4. Edit ``mysite/settings.py:36`` to match your timezone
5. Run the server: ``python manage.py runserver``
6. Open website in browser at ``http://localhost:8000/polls`` or admin at
   ``http://localhost:8000/admin`` (admin:admin)
7. Use admin to set your Site's domain name for sending (registration) emails.
   Example: ``localhost:8000``
8. Set the ``EMAIL_HOST_PASSWORD`` environment variable (in ``.bashrc``,
    ``bin/activate``, etc.), and other email-related settings.

### After initial setup ###
1. Activate the virtualenv: ``source env/bin/activate``
2. Run the server: ``python manage.py runserver``
3. Open website in browser at ``http://localhost:8000/polls`` or admin at
   ``http://localhost:8000/admin`` (admin:admin)
