.. requests-html documentation master file, created by
   sphinx-quickstart on Tue Feb 27 08:03:45 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Requests-HTML: HTML Parsing for Humans (writing Python 3)!
==========================================================


.. toctree::
   :maxdepth: 2
   :caption: Contents:



.. image:: https://travis-ci.com/psf/requests-html.svg?branch=master
    :target: https://travis-ci.com/psf/requests-html

This library intends to make parsing HTML (e.g. scraping the web) as
simple and intuitive as possible.

When using this library you automatically get:

- **Full JavaScript support**!
- *CSS Selectors* (a.k.a jQuery-style, thanks to PyQuery).
- *XPath Selectors*, for the faint of heart.
- Mocked user-agent (like a real web browser).
- Automatic following of redirects.
- Connection–pooling and cookie persistence.
- The Requests experience you know and love, with magical parsing abilities.
- **Async Support**

.. Other nice features include:

    - Markdown export of pages and elements.


Installation
============

.. code-block:: shell

    $ pipenv install requests-html
    ✨🍰✨

Only **Python 3.6** is supported.


Tutorial & Usage
================

Make a GET request to `python.org <https://python.org/>`_, using `Requests <https://docs.python-requests.org/>`_:

.. code-block:: pycon

    >>> from requests_html import HTMLSession
    >>> session = HTMLSession()

    >>> r = session.get('https://python.org/')

Or want to try our async session:

.. code-block:: pycon

    >>> from requests_html import AsyncHTMLSession
    >>> asession = AsyncHTMLSession()

    >>> r = await asession.get('https://python.org/')

But async is fun when fetching some sites at the same time:

.. code-block:: pycon

    >>> from requests_html import AsyncHTMLSession
    >>> asession = AsyncHTMLSession()

    >>> async def get_pythonorg():
    ...    r = await asession.get('https://python.org/')

    >>> async def get_reddit():
    ...    r = await asession.get('https://reddit.com/')

    >>> async def get_google():
    ...    r = await asession.get('https://google.com/')

    >>> session.run(get_pythonorg, get_reddit, get_google)

Grab a list of all links on the page, as–is (anchors excluded):

.. code-block:: pycon

    >>> r.html.links
    {'//docs.python.org/3/tutorial/', '/about/apps/', 'https://github.com/python/pythondotorg/issues', '/accounts/login/', '/dev/peps/', '/about/legal/', '//docs.python.org/3/tutorial/introduction.html#lists', '/download/alternatives', 'http://feedproxy.google.com/~r/PythonInsider/~3/kihd2DW98YY/python-370a4-is-available-for-testing.html', '/download/other/', '/downloads/windows/', 'https://mail.python.org/mailman/listinfo/python-dev', '/doc/av', 'https://devguide.python.org/', '/about/success/#engineering', 'https://wiki.python.org/moin/PythonEventsCalendar#Submitting_an_Event', 'https://www.openstack.org', '/about/gettingstarted/', 'http://feedproxy.google.com/~r/PythonInsider/~3/AMoBel8b8Mc/python-3.html', '/success-stories/industrial-light-magic-runs-python/', 'http://docs.python.org/3/tutorial/introduction.html#using-python-as-a-calculator', '/', 'http://pyfound.blogspot.com/', '/events/python-events/past/', '/downloads/release/python-2714/', 'https://wiki.python.org/moin/PythonBooks', 'http://plus.google.com/+Python', 'https://wiki.python.org/moin/', 'https://status.python.org/', '/community/workshops/', '/community/lists/', 'http://buildbot.net/', '/community/awards', 'http://twitter.com/ThePSF', 'https://docs.python.org/3/license.html', '/psf/donations/', 'http://wiki.python.org/moin/Languages', '/dev/', '/events/python-user-group/', 'https://wiki.qt.io/PySide', '/community/sigs/', 'https://wiki.gnome.org/Projects/PyGObject', 'http://www.ansible.com', 'http://www.saltstack.com', 'http://planetpython.org/', '/events/python-events', '/about/help/', '/events/python-user-group/past/', '/about/success/', '/psf-landing/', '/about/apps', '/about/', 'http://www.wxpython.org/', '/events/python-user-group/665/', 'https://www.python.org/psf/codeofconduct/', '/dev/peps/peps.rss', '/downloads/source/', '/psf/sponsorship/sponsors/', 'http://bottlepy.org', 'http://roundup.sourceforge.net/', 'http://pandas.pydata.org/', 'http://brochure.getpython.info/', 'https://bugs.python.org/', '/community/merchandise/', 'http://tornadoweb.org', '/events/python-user-group/650/', 'http://flask.pocoo.org/', '/downloads/release/python-364/', '/events/python-user-group/660/', '/events/python-user-group/638/', '/psf/', '/doc/', 'http://blog.python.org', '/events/python-events/604/', '/about/success/#government', 'http://python.org/dev/peps/', 'https://docs.python.org', 'http://feedproxy.google.com/~r/PythonInsider/~3/zVC80sq9s00/python-364-is-now-available.html', '/users/membership/', '/about/success/#arts', 'https://wiki.python.org/moin/Python2orPython3', '/downloads/', '/jobs/', 'http://trac.edgewall.org/', 'http://feedproxy.google.com/~r/PythonInsider/~3/wh73_1A-N7Q/python-355rc1-and-python-348rc1-are-now.html', '/privacy/', 'https://pypi.python.org/', 'http://www.riverbankcomputing.co.uk/software/pyqt/intro', 'http://www.scipy.org', '/community/forums/', '/about/success/#scientific', '/about/success/#software-development', '/shell/', '/accounts/signup/', 'http://www.facebook.com/pythonlang?fref=ts', '/community/', 'https://kivy.org/', '/about/quotes/', 'http://www.web2py.com/', '/community/logos/', '/community/diversity/', '/events/calendars/', 'https://wiki.python.org/moin/BeginnersGuide', '/success-stories/', '/doc/essays/', '/dev/core-mentorship/', 'http://ipython.org', '/events/', '//docs.python.org/3/tutorial/controlflow.html', '/about/success/#education', '/blogs/', '/community/irc/', 'http://pycon.blogspot.com/', '//jobs.python.org', 'http://www.pylonsproject.org/', 'http://www.djangoproject.com/', '/downloads/mac-osx/', '/about/success/#business', 'http://feedproxy.google.com/~r/PythonInsider/~3/x_c9D0S-4C4/python-370b1-is-now-available-for.html', 'http://wiki.python.org/moin/TkInter', 'https://docs.python.org/faq/', '//docs.python.org/3/tutorial/controlflow.html#defining-functions'}

Grab a list of all links on the page, in `absolute form <https://www.navegabem.com/absolute-or-relative-links.html>`_ (anchors excluded):

.. code-block:: pycon

    >>> r.html.absolute_links
    {'https://github.com/python/pythondotorg/issues', 'https://docs.python.org/3/tutorial/', 'https://www.python.org/about/success/', 'http://feedproxy.google.com/~r/PythonInsider/~3/kihd2DW98YY/python-370a4-is-available-for-testing.html', 'https://www.python.org/dev/peps/', 'https://mail.python.org/mailman/listinfo/python-dev', 'https://www.python.org/doc/', 'https://www.python.org/', 'https://www.python.org/about/', 'https://www.python.org/events/python-events/past/', 'https://devguide.python.org/', 'https://wiki.python.org/moin/PythonEventsCalendar#Submitting_an_Event', 'https://www.openstack.org', 'http://feedproxy.google.com/~r/PythonInsider/~3/AMoBel8b8Mc/python-3.html', 'https://docs.python.org/3/tutorial/introduction.html#lists', 'http://docs.python.org/3/tutorial/introduction.html#using-python-as-a-calculator', 'http://pyfound.blogspot.com/', 'https://wiki.python.org/moin/PythonBooks', 'http://plus.google.com/+Python', 'https://wiki.python.org/moin/', 'https://www.python.org/events/python-events', 'https://status.python.org/', 'https://www.python.org/about/apps', 'https://www.python.org/downloads/release/python-2714/', 'https://www.python.org/psf/donations/', 'http://buildbot.net/', 'http://twitter.com/ThePSF', 'https://docs.python.org/3/license.html', 'http://wiki.python.org/moin/Languages', 'https://docs.python.org/faq/', 'https://jobs.python.org', 'https://www.python.org/about/success/#software-development', 'https://www.python.org/about/success/#education', 'https://www.python.org/community/logos/', 'https://www.python.org/doc/av', 'https://wiki.qt.io/PySide', 'https://www.python.org/events/python-user-group/660/', 'https://wiki.gnome.org/Projects/PyGObject', 'http://www.ansible.com', 'http://www.saltstack.com', 'https://www.python.org/dev/peps/peps.rss', 'http://planetpython.org/', 'https://www.python.org/events/python-user-group/past/', 'https://docs.python.org/3/tutorial/controlflow.html#defining-functions', 'https://www.python.org/community/diversity/', 'https://docs.python.org/3/tutorial/controlflow.html', 'https://www.python.org/community/awards', 'https://www.python.org/events/python-user-group/638/', 'https://www.python.org/about/legal/', 'https://www.python.org/dev/', 'https://www.python.org/download/alternatives', 'https://www.python.org/downloads/', 'https://www.python.org/community/lists/', 'http://www.wxpython.org/', 'https://www.python.org/about/success/#government', 'https://www.python.org/psf/', 'https://www.python.org/psf/codeofconduct/', 'http://bottlepy.org', 'http://roundup.sourceforge.net/', 'http://pandas.pydata.org/', 'http://brochure.getpython.info/', 'https://www.python.org/downloads/source/', 'https://bugs.python.org/', 'https://www.python.org/downloads/mac-osx/', 'https://www.python.org/about/help/', 'http://tornadoweb.org', 'http://flask.pocoo.org/', 'https://www.python.org/users/membership/', 'http://blog.python.org', 'https://www.python.org/privacy/', 'https://www.python.org/about/gettingstarted/', 'http://python.org/dev/peps/', 'https://www.python.org/about/apps/', 'https://docs.python.org', 'https://www.python.org/success-stories/', 'https://www.python.org/community/forums/', 'http://feedproxy.google.com/~r/PythonInsider/~3/zVC80sq9s00/python-364-is-now-available.html', 'https://www.python.org/community/merchandise/', 'https://www.python.org/about/success/#arts', 'https://wiki.python.org/moin/Python2orPython3', 'http://trac.edgewall.org/', 'http://feedproxy.google.com/~r/PythonInsider/~3/wh73_1A-N7Q/python-355rc1-and-python-348rc1-are-now.html', 'https://pypi.python.org/', 'https://www.python.org/events/python-user-group/650/', 'http://www.riverbankcomputing.co.uk/software/pyqt/intro', 'https://www.python.org/about/quotes/', 'https://www.python.org/downloads/windows/', 'https://www.python.org/events/calendars/', 'http://www.scipy.org', 'https://www.python.org/community/workshops/', 'https://www.python.org/blogs/', 'https://www.python.org/accounts/signup/', 'https://www.python.org/events/', 'https://kivy.org/', 'http://www.facebook.com/pythonlang?fref=ts', 'http://www.web2py.com/', 'https://www.python.org/psf/sponsorship/sponsors/', 'https://www.python.org/community/', 'https://www.python.org/download/other/', 'https://www.python.org/psf-landing/', 'https://www.python.org/events/python-user-group/665/', 'https://wiki.python.org/moin/BeginnersGuide', 'https://www.python.org/accounts/login/', 'https://www.python.org/downloads/release/python-364/', 'https://www.python.org/dev/core-mentorship/', 'https://www.python.org/about/success/#business', 'https://www.python.org/community/sigs/', 'https://www.python.org/events/python-user-group/', 'http://ipython.org', 'https://www.python.org/shell/', 'https://www.python.org/community/irc/', 'https://www.python.org/about/success/#engineering', 'http://www.pylonsproject.org/', 'http://pycon.blogspot.com/', 'https://www.python.org/about/success/#scientific', 'https://www.python.org/doc/essays/', 'http://www.djangoproject.com/', 'https://www.python.org/success-stories/industrial-light-magic-runs-python/', 'http://feedproxy.google.com/~r/PythonInsider/~3/x_c9D0S-4C4/python-370b1-is-now-available-for.html', 'http://wiki.python.org/moin/TkInter', 'https://www.python.org/jobs/', 'https://www.python.org/events/python-events/604/'}

Select an :class:`Element <Element>` with a CSS Selector (`learn more <https://www.w3schools.com/cssref/css_selectors.asp>`_):

.. code-block:: pycon

    >>> about = r.html.find('#about', first=True)

Grab an :class:`Element <Element>`'s text contents:

.. code-block:: pycon

    >>> print(about.text)
    About
    Applications
    Quotes
    Getting Started
    Help
    Python Brochure

Introspect an :class:`Element <Element>`'s attributes (`learn more <https://developer.mozilla.org/en-US/docs/Web/HTML/Attributes>`_):

.. code-block:: pycon

    >>> about.attrs
    {'id': 'about', 'class': ('tier-1', 'element-1'), 'aria-haspopup': 'true'}

Render out an :class:`Element <Element>`'s HTML:

.. code-block:: pycon

    >>> about.html
    '<li aria-haspopup="true" class="tier-1 element-1 " id="about">\n<a class="" href="/about/" title="">About</a>\n<ul aria-hidden="true" class="subnav menu" role="menu">\n<li class="tier-2 element-1" role="treeitem"><a href="/about/apps/" title="">Applications</a></li>\n<li class="tier-2 element-2" role="treeitem"><a href="/about/quotes/" title="">Quotes</a></li>\n<li class="tier-2 element-3" role="treeitem"><a href="/about/gettingstarted/" title="">Getting Started</a></li>\n<li class="tier-2 element-4" role="treeitem"><a href="/about/help/" title="">Help</a></li>\n<li class="tier-2 element-5" role="treeitem"><a href="http://brochure.getpython.info/" title="">Python Brochure</a></li>\n</ul>\n</li>'

Crab an :class:`Element <Element>`'s root tag name:

.. code-block:: pycon

   >>> about.tag
   'li'

Show the line number that an :class:`Element <Element>`'s root tag located in:

.. code-block:: pycon

    >>> about.lineno
    249

Select an :class:`Element <Element>` list within an :class:`Element <Element>`:

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

XPath is also supported (`learn more <https://msdn.microsoft.com/en-us/library/ms256086(v=vs.110).aspx>`_):

.. code-block:: pycon

   >>> r.html.xpath('a')
   [<Element 'a' class='btn' href='https://help.github.com/articles/supported-browsers'>]

You can also select only elements containing certain text:

.. code-block:: pycon

    >>> r = session.get('http://python-requests.org/')
    >>> r.html.find('a', containing='kenneth')
    [<Element 'a' href='http://kennethreitz.com/pages/open-projects.html'>, <Element 'a' href='http://kennethreitz.org/'>, <Element 'a' href='https://twitter.com/kennethreitz' class=('twitter-follow-button',) data-show-count='false'>, <Element 'a' class=('reference', 'internal') href='dev/contributing/#kenneth-reitz-s-code-style'>]


JavaScript Support
==================

Let's grab some text that's rendered by JavaScript:

.. code-block:: pycon

    >>> r = session.get('http://python-requests.org/')

    >>> r.html.render()

    >>> r.html.search('Python 2 will retire in only {months} months!')['months']
    '<time>25</time>'

Or you can do this async also:

.. code-block:: pycon

    >>> r = asession.get('http://python-requests.org/')

    >>> await r.html.arender()

    >>> r.html.search('Python 2 will retire in only {months} months!')['months']
    '<time>25</time>'

Note, the first time you ever run the ``render()`` method, it will download
Chromium into your home directory (e.g. ``~/.pyppeteer/``). This only happens
once. You may also need to install a few `Linux packages <https://github.com/miyakogi/pyppeteer/issues/60>`_ to get pyppeteer working.

Pagination
==========

There's also intelligent pagination support (always improving):

.. code-block:: pycon

    >>> r = session.get('https://reddit.com')
    >>> for html in r.html:
    ...     print(html)
    <HTML url='https://www.reddit.com/'>
    <HTML url='https://www.reddit.com/?count=25&after=t3_81puu5'>
    <HTML url='https://www.reddit.com/?count=50&after=t3_81nevg'>
    <HTML url='https://www.reddit.com/?count=75&after=t3_81lqtp'>
    <HTML url='https://www.reddit.com/?count=100&after=t3_81k1c8'>
    <HTML url='https://www.reddit.com/?count=125&after=t3_81p438'>
    <HTML url='https://www.reddit.com/?count=150&after=t3_81nrcd'>
    …

For `async` pagination use the new `async for`:

.. code-block:: pycon

    >>> r = await asession.get('https://reddit.com')
    >>> async for html in r.html:
    ...     print(html)
    <HTML url='https://www.reddit.com/'>
    <HTML url='https://www.reddit.com/?count=25&after=t3_81puu5'>
    …

You can also just request the next URL easily:

.. code-block:: pycon

    >>> r = session.get('https://reddit.com')
    >>> r.html.next()
    'https://www.reddit.com/?count=25&after=t3_81pm82'

Using without Requests
======================

You can also use this library without Requests:

.. code-block:: pycon

    >>> from requests_html import HTML
    >>> doc = """<a href='https://httpbin.org'>"""

    >>> html = HTML(html=doc)
    >>> html.links
    {'https://httpbin.org'}

You can also render JavaScript pages without Requests:

.. code-block:: pycon

    # ^^ proceeding from above ^^
    >>> script = """
            () => {
                return {
                    width: document.documentElement.clientWidth,
                    height: document.documentElement.clientHeight,
                    deviceScaleFactor: window.devicePixelRatio,
                }
            }
        """
    >>> val = html.render(script=script, reload=False)

    >>> print(val)
    {'width': 800, 'height': 600, 'deviceScaleFactor': 1}

    >>> print(html.html)
    <html><head></head><body><a href="https://httpbin.org"></a></body></html>

For using `arender` just pass `async_=True` to HTML.

.. code-block:: pycon

    # ^^ using above script ^^
    >>> html = HTML(html=doc, async_=True)
    >>> val = await html.arender(script=script, reload=False)
    >>> print(val)
    {'width': 800, 'height': 600, 'deviceScaleFactor': 1}


API Documentation
=================

Main Classes
------------

.. module:: requests_html

These classes are the main interface to ``requests-html``:


.. autoclass:: HTML
    :inherited-members:

.. autoclass:: Element
    :inherited-members:

Utility Functions
-----------------

.. autofunction:: user_agent

HTML Sessions
-------------

These sessions are for making HTTP requests:

.. autoclass:: HTMLSession
    :inherited-members:


.. autoclass:: AsyncHTMLSession
    :inherited-members:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
