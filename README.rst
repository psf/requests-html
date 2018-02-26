Requests-HTML: HTML Parsing for Humans™
=======================================

.. image:: https://travis-ci.org/kennethreitz/requests-html.svg?branch=master
    :target: https://travis-ci.org/kennethreitz/requests-html

This library intends to make parsing HTML (e.g. scraping the web) as
simple and intuitive as possible.

When using this library you automatically get:

- CSS Selectors (a.k.a jQuery-style, thanks to PyQuery).
- XPath Selectors, for the faint at heart.
- Mocked user-agent (like a real web browser).
- Automatic following of redirects.
- Connection–pooling and cookie persistience.
- The Requests experience you know and love, with magical parsing abilities.

.. Other nice features include:

    - Markdown export of pages and elements.


Usage
=====

Make a GET request to 'python.org', using Requests:

.. code-block:: pycon

    >>> import requests_html
    >>> session = requests_html.Session()

    >>> r = session.get('https://python.org/')

Grab a list of all links on the page, as–is (anchors excluded):

.. code-block:: pycon

    >>> r.html.links
    {'/users/membership/', '/about/gettingstarted/', 'http://feedproxy.google.com/~r/PythonInsider/~3/zVC80sq9s00/python-364-is-now-available.html', '/about/success/', 'http://flask.pocoo.org/', 'http://www.djangoproject.com/', '/blogs/', ... '/psf-landing/', 'https://wiki.python.org/moin/PythonBooks'}

Grab a list of all links on the page, in absolute form (anchors excluded):

.. code-block:: pycon

    >>> r.html.absolute_links
    {'http://feedproxy.google.com/~r/PythonInsider/~3/zVC80sq9s00/python-364-is-now-available.html', 'https://www.python.org/downloads/mac-osx/', 'http://flask.pocoo.org/', 'https://www.python.org/docs.python.org/3/tutorial/', 'http://www.djangoproject.com/', 'https://wiki.python.org/moin/BeginnersGuide', 'https://www.python.org/about/success/', 'http://twitter.com/ThePSF', 'https://www.python.org/events/python-user-group/634/', ..., 'https://wiki.python.org/moin/PythonBooks'}

Select an element with a CSS Selector:

.. code-block:: pycon

    >>> about = r.html.find('#about', first=True)

Grab an element's text contents:

.. code-block:: pycon

    >>> print(about.text)
    About
    Applications
    Quotes
    Getting Started
    Help
    Python Brochure

Introspect an Element's attributes:

.. code-block:: pycon

    >>> about.attrs
    {'id': 'about', 'class': ('tier-1', 'element-1'), 'aria-haspopup': 'true'}

Select Elements within Elements:

.. code-block:: pycon

    >>> about.find('a')
    [<Element 'a' href='/about/' title='' class=''>, <Element 'a' href='/about/apps/' title=''>, <Element 'a' href='/about/quotes/' title=''>, <Element 'a' href='/about/gettingstarted/' title=''>, <Element 'a' href='/about/help/' title=''>, <Element 'a' href='http://brochure.getpython.info/' title=''>]

Search for links within an element:

.. code-block:: pycon

    >>> about.absolute_links
    {'http://brochure.getpython.info/', 'https://www.python.org/about/gettingstarted/', 'https://www.python.org/about/', 'https://www.python.org/about/quotes/', 'https://www.python.org/about/help/', 'https://www.python.org/about/apps/'}


Search for text on the page:

.. code-block:: pycon

    >>> r.html.search('Python is a {} language')[0]
    programming

More complex CSS Selector example (copied from Chrome dev tools):

.. code-block:: pycon

    >>> r = session.get('https://github.com/')
    >>> sel = 'body > div.application-main > div.jumbotron.jumbotron-codelines > div > div > div.col-md-7.text-center.text-md-left > p'

    >>> print(r.html.find(sel, first=True).text)
    GitHub is a development platform inspired by the way you work. From open source to business, you can host and review code, manage projects, and build software alongside millions of other developers.

XPath is also supported:

.. code-block:: pycon

   >>> r.html.xpath('a')
   [<Element 'a' class='btn' href='https://help.github.com/articles/supported-browsers'>]

Other Fun (with Markdown)
=========================

If you'd like to take an element and convert it to Markdown, for example, use `html2text`, by Aaron Swartz:

.. code-block:: shell

    $ pipenv install html2text

.. code-block:: pycon

    >>> from html2text import HTML2Text
    >>> h = html2text.HTML2Text()
    >>> print(h.handle(about.html))
    * [About](/about/)

      * [Applications](/about/apps/)
      * [Quotes](/about/quotes/)
      * [Getting Started](/about/gettingstarted/)
      * [Help](/about/help/)
      * [Python Brochure](http://brochure.getpython.info/)


Installation
============

.. code-block:: shell

    $ pipenv install requests-html
    ✨🍰✨

Only Python 3 is supported.
