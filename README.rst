=====
Simhash
=====

Quite a silly project to find near-duplicates of texts posted to this service. The problem with other implementations is they assume you have all texts in advance and can do a conventional sort after generating all the simhashes. However if you are adding new texts to an existing collection and want to check each time for near-duplicates, you don't want to do an N log N sort for every new element. It should be possible to check each new element in log N time by inserting into an already sorted list. Probably a very slow log N though.

We will only compare to hashes with same source and method. Based on source and guid, source system can work out what the two texts are. Source system can send some params which change method.

Quick start
-----------

1. Add "simhash_app" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'simhash_app',
    ]

2. Include the simhash URLconf in your project urls.py like this::

    path('', include('simhash_app.urls')),

3. Run `python manage.py migrate` to create the simhash models.

4. Start the development server and POST a text to http://127.0.0.1:8000/hashes/

5. Response will tell you how similar it is to existing texts.
