Requests-HTML: HTML Parsing for Humans™
=======================================

This library intends to make parsing HTML (e.g. scraping the web) as
simple and intuitive as possible.

When using this library you automatically get:

- jQuery selectors (thanks to PyQuery).
- Mocked user-agent (like a real web browser).
- Automatic following of redirects.
- Connection–pooling and cookie persistience.
- The Requests experience you know and love, with magic parsing abilities.

Other nice features include:

- Markdown export of pages and elements.


Usage
=====

.. code-block:: pycon

    >>> from requests_html import session

    >>> r = session.get('https://python.org/')

    >>> r.html.links
    {'/users/membership/', '/about/gettingstarted/', 'http://feedproxy.google.com/~r/PythonInsider/~3/zVC80sq9s00/python-364-is-now-available.html', '/about/success/', 'http://flask.pocoo.org/', 'http://www.djangoproject.com/', '/blogs/', ... '/psf-landing/', 'https://wiki.python.org/moin/PythonBooks'}

    >>> r.html.absolute_links
    {'http://feedproxy.google.com/~r/PythonInsider/~3/zVC80sq9s00/python-364-is-now-available.html', 'https://www.python.org/downloads/mac-osx/', 'http://flask.pocoo.org/', 'https://www.python.org//docs.python.org/3/tutorial/', 'http://www.djangoproject.com/', 'https://wiki.python.org/moin/BeginnersGuide', 'https://www.python.org//docs.python.org/3/tutorial/controlflow.html#defining-functions', 'https://www.python.org/about/success/', 'http://twitter.com/ThePSF', 'https://www.python.org/events/python-user-group/634/', ..., 'https://wiki.python.org/moin/PythonBooks'}

    >>> about = r.html.find('#about')[0]
    >>> print(about.text)
    About
    Applications
    Quotes
    Getting Started
    Help
    Python Brochure

    >>> print(about.markdown)

    * [About](/about/)

      * [Applications](/about/apps/)
      * [Quotes](/about/quotes/)
      * [Getting Started](/about/gettingstarted/)
      * [Help](/about/help/)
      * [Python Brochure](http://brochure.getpython.info/)

    >>> about.attrs
    {'id': 'about', 'class': 'tier-1 element-1  ', 'aria-haspopup': 'true'}

    >>> about.find('a')
    [<Element 'a' href='/about/' title='' class=''>, <Element 'a' href='/about/apps/' title=''>, <Element 'a' href='/about/quotes/' title=''>, <Element 'a' href='/about/gettingstarted/' title=''>, <Element 'a' href='/about/help/' title=''>, <Element 'a' href='http://brochure.getpython.info/' title=''>]

    >>> r.html.search('Python is a {} language')[0]
    programming

Installation
============

.. code-block:: shell

    $ pipenv install requests-html
    ✨🍰✨

