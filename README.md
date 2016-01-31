django-poll-app
===============

The solution to https://docs.djangoproject.com/en/dev/intro/tutorial01/

Getting Started
---------------

### Initial Setup ###
1. Make a new virtualenv: ``virtualenv env``
2. Activate the virtualenv: ``source env/bin/activate``
3. Install Django: ``pip install Django``
4. Put the ``polls/`` directory inside your project directory. If you don't
   have one, ``django-admin.py startproject mysite``.
5. Edit ``mysite/settings.py`` and put ``polls`` in ``INSTALLED_APPS``. 
6. Edit ``mysite/settings.py:36`` to match your timezone
7. Run the server: ``python manage.py runserver``
8. Open website in browser at ``http://localhost:8000/polls`` or admin at
   ``http://localhost:8000/admin`` (admin:admin)

### After initial setup ###
1. Activate the virtualenv: ``source env/bin/activate``
2. Run the server: ``python manage.py runserver``
3. Open website in browser at ``http://localhost:8000/polls`` or admin at
   ``http://localhost:8000/admin`` (admin:admin)
