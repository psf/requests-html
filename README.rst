Requests-HTML: HTML Parsing for Humans™
=======================================

.. image:: https://farm5.staticflickr.com/4695/39152770914_a3ab8af40d_k_d.jpg

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


Tutorial & Usage
================

Make a GET request to 'python.org', using Requests:

.. code-block:: pycon

    >>> from requests_html import HTMLSession
    >>> session = HTMLSession()
    >>> r = session.get('https://python.org/')

Try async and get some sites at the same time:

.. code-block:: pycon

    >>> from requests_html import AsyncHTMLSession
    >>> asession = AsyncHTMLSession()
    >>> async def get_pythonorg():
    ...     r = await asession.get('https://python.org/')
    ...     return r
    ...
    >>> async def get_reddit():
    ...    r = await asession.get('https://reddit.com/')
    ...    return r
    ...
    >>> async def get_google():
    ...    r = await asession.get('https://google.com/')
    ...    return r
    ...
    >>> results = asession.run(get_pythonorg, get_reddit, get_google)
    >>> results # check the requests all returned a 200 (success) code
    [<Response [200]>, <Response [200]>, <Response [200]>]
    >>> # Each item in the results list is a response object and can be interacted with as such
    >>> for result in results: 
    ...     print(result.html.url)
    ... 
    https://www.python.org/
    https://www.google.com/
    https://www.reddit.com/

Note that the order of the objects in the results list represents the order they were returned in, not the order that the coroutines are passed to the ``run`` method, which is shown in the example by the order being different. 

Grab a list of all links on the page, as–is (anchors excluded):

.. code-block:: pycon

    >>> r.html.links
    {'//docs.python.org/3/tutorial/', '/about/apps/', 'https://github.com/python/pythondotorg/issues', '/accounts/login/', '/dev/peps/', '/about/legal/', '//docs.python.org/3/tutorial/introduction.html#lists', '/download/alternatives', 'http://feedproxy.google.com/~r/PythonInsider/~3/kihd2DW98YY/python-370a4-is-available-for-testing.html', '/download/other/', '/downloads/windows/', 'https://mail.python.org/mailman/listinfo/python-dev', '/doc/av', 'https://devguide.python.org/', '/about/success/#engineering', 'https://wiki.python.org/moin/PythonEventsCalendar#Submitting_an_Event', 'https://www.openstack.org', '/about/gettingstarted/', 'http://feedproxy.google.com/~r/PythonInsider/~3/AMoBel8b8Mc/python-3.html', '/success-stories/industrial-light-magic-runs-python/', 'http://docs.python.org/3/tutorial/introduction.html#using-python-as-a-calculator', '/', 'http://pyfound.blogspot.com/', '/events/python-events/past/', '/downloads/release/python-2714/', 'https://wiki.python.org/moin/PythonBooks', 'http://plus.google.com/+Python', 'https://wiki.python.org/moin/', 'https://status.python.org/', '/community/workshops/', '/community/lists/', 'http://buildbot.net/', '/community/awards', 'http://twitter.com/ThePSF', 'https://docs.python.org/3/license.html', '/psf/donations/', 'http://wiki.python.org/moin/Languages', '/dev/', '/events/python-user-group/', 'https://wiki.qt.io/PySide', '/community/sigs/', 'https://wiki.gnome.org/Projects/PyGObject', 'http://www.ansible.com', 'http://www.saltstack.com', 'http://planetpython.org/', '/events/python-events', '/about/help/', '/events/python-user-group/past/', '/about/success/', '/psf-landing/', '/about/apps', '/about/', 'http://www.wxpython.org/', '/events/python-user-group/665/', 'https://www.python.org/psf/codeofconduct/', '/dev/peps/peps.rss', '/downloads/source/', '/psf/sponsorship/sponsors/', 'http://bottlepy.org', 'http://roundup.sourceforge.net/', 'http://pandas.pydata.org/', 'http://brochure.getpython.info/', 'https://bugs.python.org/', '/community/merchandise/', 'http://tornadoweb.org', '/events/python-user-group/650/', 'http://flask.pocoo.org/', '/downloads/release/python-364/', '/events/python-user-group/660/', '/events/python-user-group/638/', '/psf/', '/doc/', 'http://blog.python.org', '/events/python-events/604/', '/about/success/#government', 'http://python.org/dev/peps/', 'https://docs.python.org', 'http://feedproxy.google.com/~r/PythonInsider/~3/zVC80sq9s00/python-364-is-now-available.html', '/users/membership/', '/about/success/#arts', 'https://wiki.python.org/moin/Python2orPython3', '/downloads/', '/jobs/', 'http://trac.edgewall.org/', 'http://feedproxy.google.com/~r/PythonInsider/~3/wh73_1A-N7Q/python-355rc1-and-python-348rc1-are-now.html', '/privacy/', 'https://pypi.python.org/', 'http://www.riverbankcomputing.co.uk/software/pyqt/intro', 'http://www.scipy.org', '/community/forums/', '/about/success/#scientific', '/about/success/#software-development', '/shell/', '/accounts/signup/', 'http://www.facebook.com/pythonlang?fref=ts', '/community/', 'https://kivy.org/', '/about/quotes/', 'http://www.web2py.com/', '/community/logos/', '/community/diversity/', '/events/calendars/', 'https://wiki.python.org/moin/BeginnersGuide', '/success-stories/', '/doc/essays/', '/dev/core-mentorship/', 'http://ipython.org', '/events/', '//docs.python.org/3/tutorial/controlflow.html', '/about/success/#education', '/blogs/', '/community/irc/', 'http://pycon.blogspot.com/', '//jobs.python.org', 'http://www.pylonsproject.org/', 'http://www.djangoproject.com/', '/downloads/mac-osx/', '/about/success/#business', 'http://feedproxy.google.com/~r/PythonInsider/~3/x_c9D0S-4C4/python-370b1-is-now-available-for.html', 'http://wiki.python.org/moin/TkInter', 'https://docs.python.org/faq/', '//docs.python.org/3/tutorial/controlflow.html#defining-functions'}

Grab a list of all links on the page, in absolute form (anchors excluded):

.. code-block:: pycon

    >>> r.html.absolute_links
    {'https://github.com/python/pythondotorg/issues', 'https://docs.python.org/3/tutorial/', 'https://www.python.org/about/success/', 'http://feedproxy.google.com/~r/PythonInsider/~3/kihd2DW98YY/python-370a4-is-available-for-testing.html', 'https://www.python.org/dev/peps/', 'https://mail.python.org/mailman/listinfo/python-dev', 'https://www.python.org/doc/', 'https://www.python.org/', 'https://www.python.org/about/', 'https://www.python.org/events/python-events/past/', 'https://devguide.python.org/', 'https://wiki.python.org/moin/PythonEventsCalendar#Submitting_an_Event', 'https://www.openstack.org', 'http://feedproxy.google.com/~r/PythonInsider/~3/AMoBel8b8Mc/python-3.html', 'https://docs.python.org/3/tutorial/introduction.html#lists', 'http://docs.python.org/3/tutorial/introduction.html#using-python-as-a-calculator', 'http://pyfound.blogspot.com/', 'https://wiki.python.org/moin/PythonBooks', 'http://plus.google.com/+Python', 'https://wiki.python.org/moin/', 'https://www.python.org/events/python-events', 'https://status.python.org/', 'https://www.python.org/about/apps', 'https://www.python.org/downloads/release/python-2714/', 'https://www.python.org/psf/donations/', 'http://buildbot.net/', 'http://twitter.com/ThePSF', 'https://docs.python.org/3/license.html', 'http://wiki.python.org/moin/Languages', 'https://docs.python.org/faq/', 'https://jobs.python.org', 'https://www.python.org/about/success/#software-development', 'https://www.python.org/about/success/#education', 'https://www.python.org/community/logos/', 'https://www.python.org/doc/av', 'https://wiki.qt.io/PySide', 'https://www.python.org/events/python-user-group/660/', 'https://wiki.gnome.org/Projects/PyGObject', 'http://www.ansible.com', 'http://www.saltstack.com', 'https://www.python.org/dev/peps/peps.rss', 'http://planetpython.org/', 'https://www.python.org/events/python-user-group/past/', 'https://docs.python.org/3/tutorial/controlflow.html#defining-functions', 'https://www.python.org/community/diversity/', 'https://docs.python.org/3/tutorial/controlflow.html', 'https://www.python.org/community/awards', 'https://www.python.org/events/python-user-group/638/', 'https://www.python.org/about/legal/', 'https://www.python.org/dev/', 'https://www.python.org/download/alternatives', 'https://www.python.org/downloads/', 'https://www.python.org/community/lists/', 'http://www.wxpython.org/', 'https://www.python.org/about/success/#government', 'https://www.python.org/psf/', 'https://www.python.org/psf/codeofconduct/', 'http://bottlepy.org', 'http://roundup.sourceforge.net/', 'http://pandas.pydata.org/', 'http://brochure.getpython.info/', 'https://www.python.org/downloads/source/', 'https://bugs.python.org/', 'https://www.python.org/downloads/mac-osx/', 'https://www.python.org/about/help/', 'http://tornadoweb.org', 'http://flask.pocoo.org/', 'https://www.python.org/users/membership/', 'http://blog.python.org', 'https://www.python.org/privacy/', 'https://www.python.org/about/gettingstarted/', 'http://python.org/dev/peps/', 'https://www.python.org/about/apps/', 'https://docs.python.org', 'https://www.python.org/success-stories/', 'https://www.python.org/community/forums/', 'http://feedproxy.google.com/~r/PythonInsider/~3/zVC80sq9s00/python-364-is-now-available.html', 'https://www.python.org/community/merchandise/', 'https://www.python.org/about/success/#arts', 'https://wiki.python.org/moin/Python2orPython3', 'http://trac.edgewall.org/', 'http://feedproxy.google.com/~r/PythonInsider/~3/wh73_1A-N7Q/python-355rc1-and-python-348rc1-are-now.html', 'https://pypi.python.org/', 'https://www.python.org/events/python-user-group/650/', 'http://www.riverbankcomputing.co.uk/software/pyqt/intro', 'https://www.python.org/about/quotes/', 'https://www.python.org/downloads/windows/', 'https://www.python.org/events/calendars/', 'http://www.scipy.org', 'https://www.python.org/community/workshops/', 'https://www.python.org/blogs/', 'https://www.python.org/accounts/signup/', 'https://www.python.org/events/', 'https://kivy.org/', 'http://www.facebook.com/pythonlang?fref=ts', 'http://www.web2py.com/', 'https://www.python.org/psf/sponsorship/sponsors/', 'https://www.python.org/community/', 'https://www.python.org/download/other/', 'https://www.python.org/psf-landing/', 'https://www.python.org/events/python-user-group/665/', 'https://wiki.python.org/moin/BeginnersGuide', 'https://www.python.org/accounts/login/', 'https://www.python.org/downloads/release/python-364/', 'https://www.python.org/dev/core-mentorship/', 'https://www.python.org/about/success/#business', 'https://www.python.org/community/sigs/', 'https://www.python.org/events/python-user-group/', 'http://ipython.org', 'https://www.python.org/shell/', 'https://www.python.org/community/irc/', 'https://www.python.org/about/success/#engineering', 'http://www.pylonsproject.org/', 'http://pycon.blogspot.com/', 'https://www.python.org/about/success/#scientific', 'https://www.python.org/doc/essays/', 'http://www.djangoproject.com/', 'https://www.python.org/success-stories/industrial-light-magic-runs-python/', 'http://feedproxy.google.com/~r/PythonInsider/~3/x_c9D0S-4C4/python-370b1-is-now-available-for.html', 'http://wiki.python.org/moin/TkInter', 'https://www.python.org/jobs/', 'https://www.python.org/events/python-events/604/'}

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

Render out an Element's HTML:

.. code-block:: pycon

    >>> about.html
    '<li aria-haspopup="true" class="tier-1 element-1 " id="about">\n<a class="" href="/about/" title="">About</a>\n<ul aria-hidden="true" class="subnav menu" role="menu">\n<li class="tier-2 element-1" role="treeitem"><a href="/about/apps/" title="">Applications</a></li>\n<li class="tier-2 element-2" role="treeitem"><a href="/about/quotes/" title="">Quotes</a></li>\n<li class="tier-2 element-3" role="treeitem"><a href="/about/gettingstarted/" title="">Getting Started</a></li>\n<li class="tier-2 element-4" role="treeitem"><a href="/about/help/" title="">Help</a></li>\n<li class="tier-2 element-5" role="treeitem"><a href="http://brochure.getpython.info/" title="">Python Brochure</a></li>\n</ul>\n</li>'



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

   >>> r.html.xpath('/html/body/div[1]/a')
   [<Element 'a' class=('px-2', 'py-4', 'show-on-focus', 'js-skip-to-content') href='#start-of-content' tabindex='1'>]


JavaScript Support
==================

Let's grab some text that's rendered by JavaScript. Until 2020, the Python 2.7 countdown clock (https://pythonclock.org) will serve as a good test page:

.. code-block:: pycon

    >>> r = session.get('https://pythonclock.org')

Let's try and see the dynamically rendered code (The countdown clock). To do that quickly at first, we'll search between the last text we see before it ('Python 2.7 will retire in...') and the first text we see after it ('Enable Guido Mode').

.. code-block:: pycon

	>>> r.html.search('Python 2.7 will retire in...{}Enable Guido Mode')[0]
	'</h1>\n        </div>\n        <div class="python-27-clock"></div>\n        <div class="center">\n            <div class="guido-button-block">\n                <button class="js-guido-mode guido-button">'

Notice the clock is missing. The ``render()`` method takes the response and renders the dynamic content just like a web browser would.

.. code-block:: pycon

    >>> r.html.render()
    >>> r.html.search('Python 2.7 will retire in...{}Enable Guido Mode')[0]
    '</h1>\n        </div>\n        <div class="python-27-clock is-countdown"><span class="countdown-row countdown-show6"><span class="countdown-section"><span class="countdown-amount">1</span><span class="countdown-period">Year</span></span><span class="countdown-section"><span class="countdown-amount">2</span><span class="countdown-period">Months</span></span><span class="countdown-section"><span class="countdown-amount">28</span><span class="countdown-period">Days</span></span><span class="countdown-section"><span class="countdown-amount">16</span><span class="countdown-period">Hours</span></span><span class="countdown-section"><span class="countdown-amount">52</span><span class="countdown-period">Minutes</span></span><span class="countdown-section"><span class="countdown-amount">46</span><span class="countdown-period">Seconds</span></span></span></div>\n        <div class="center">\n            <div class="guido-button-block">\n                <button class="js-guido-mode guido-button">'

Let's clean it up a bit. This step is not needed, it just makes it a bit easier to visualize the returned html to see what we need to target to extract our required information. 

.. code-block:: pycon

	>>> from pprint import pprint
	>>> pprint(r.html.search('Python 2.7 will retire in...{}Enable')[0])
	('</h1>\n'
 '        </div>\n'
 '        <div class="python-27-clock is-countdown"><span class="countdown-row '
 'countdown-show6"><span class="countdown-section"><span '
 'class="countdown-amount">1</span><span '
 'class="countdown-period">Year</span></span><span '
 'class="countdown-section"><span class="countdown-amount">2</span><span '
 'class="countdown-period">Months</span></span><span '
 'class="countdown-section"><span class="countdown-amount">28</span><span '
 'class="countdown-period">Days</span></span><span '
 'class="countdown-section"><span class="countdown-amount">16</span><span '
 'class="countdown-period">Hours</span></span><span '
 'class="countdown-section"><span class="countdown-amount">52</span><span '
 'class="countdown-period">Minutes</span></span><span '
 'class="countdown-section"><span class="countdown-amount">46</span><span '
 'class="countdown-period">Seconds</span></span></span></div>\n'
 '        <div class="center">\n'
 '            <div class="guido-button-block">\n'
 '                <button class="js-guido-mode guido-button">')

The rendered html has all the same methods and attributes as above. Let's extract just the data that we want out of the clock into something easy to use elsewhere and introspect like a dictionary.

.. code-block:: pycon
	
	>>> periods = [element.text for element in r.html.find('.countdown-period')]
	>>> amounts = [element.text for element in r.html.find('.countdown-amount')]
	>>> countdown_data = dict(zip(periods, amounts))
	>>> countdown_data
	{'Year': '1', 'Months': '2', 'Days': '5', 'Hours': '23', 'Minutes': '34', 'Seconds': '37'}

Or you can do this async also:

.. code-block:: pycon

    >>> async def get_pyclock():
    ...     r = await asession.get('https://pythonclock.org/')
    ...     await r.html.arender()
    ...     return r
    ...
    >>> results = asession.run(get_pyclock, get_pyclock, get_pyclock)

The rest of the code operates the same way as the synchronous version except that ``results`` is a list containing multiple response objects however the same basic processes can be applied as above to extract the data you want. 

Note, the first time you ever run the ``render()`` method, it will download
Chromium into your home directory (e.g. ``~/.pyppeteer/``). This only happens
once.

Using without Requests
======================

You can also use this library without Requests:

.. code-block:: pycon

    >>> from requests_html import HTML
    >>> doc = """<a href='https://httpbin.org'>"""
    >>> html = HTML(html=doc)
    >>> html.links
    {'https://httpbin.org'}


Installation
============

.. code-block:: shell

    $ pipenv install requests-html
    ✨🍰✨

Only **Python 3.6 and above** is supported.
