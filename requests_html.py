from urllib.parse import urlparse, urlunparse

import requests
from pyquery import PyQuery

from fake_useragent import UserAgent
from lxml import etree
from lxml.html.soupparser import fromstring
from parse import search as parse_search
from parse import findall
from w3lib.encoding import html_to_unicode

try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtWebEngineWidgets import QWebEngineView
except ImportError:
    pass


DEFAULT_ENCODING = 'utf-8'

useragent = UserAgent()

class HTMLResponse(requests.Response):
    """An HTML-enabled :class:`Response <Response>` object.
    Same as Requests class:`Response <Response>` object, but with an
    intelligent ``.html`` property added.
    """

    def __init__(self, *args, **kwargs):
        super(HTMLResponse, self).__init__(*args, **kwargs)
        self._html = None

    @property
    def html(self):
        if self._html:
            return self._html

        self._html = HTML(url=self.url, html=self.text, default_encoding=self.encoding)
        return self._html

    @classmethod
    def _from_response(cls, response):
        html_r = cls()
        html_r.__dict__.update(response.__dict__)
        return html_r



class BaseParser:
    """A basic HTML/Element Parser, for Humans."""

    def __init__(self, *, element, default_encoding=None, html=None, url):
        self.element = element
        self.url = url
        self.skip_anchors = True
        self.default_encoding = default_encoding
        self._encoding = None
        self._html = html

    @property
    def html(self):
        """Unicode representation of the HTML content."""
        if self._html:
            return self._html
        else:
            return etree.tostring(self.element, encoding='unicode').strip()

    @html.setter
    def set_html(self, html):
        """Property setter for self.html."""
        self._html = html

    @property
    def encoding(self):
        """The encoding string to be used, extracted from the HTML and
        :class:`HTMLResponse <HTMLResponse>` headers.
        """
        if self._encoding:
            return self._encoding

        # Scan meta tags for chaset.
        if self._html:
            self._encoding = html_to_unicode(self.default_encoding, self.html.encode(DEFAULT_ENCODING))[0]

        return self._encoding if self._encoding else self.default_encoding

    @property
    def pq(self):
        """PyQuery representation of the :class:`Element <Element>` or :class:`HTML <HTML>`."""
        return PyQuery(self.element)

    @property
    def lxml(self):
        return fromstring(self.html)

    @property
    def text(self):
        """The text content of the :class:`Element <Element>` or :class:`HTML <HTML>`."""
        return self.pq.text()

    @property
    def full_text(self):
        """The full text content (including links) of the :class:`Element <Element>` or :class:`HTML <HTML>`.."""
        return self.lxml.text_content()

    def find(self, selector, first=False, _encoding=None):
        """Given a jQuery selector, returns a list of :class:`Element <Element>` objects.

        If ``first`` is ``True``, only returns the first :class:`Element <Element>` found."""
        def gen():
            for found in self.pq(selector):
                yield Element(element=found, url=self.url, default_encoding=_encoding or self.encoding)

        c = [g for g in gen()]

        if first:
            try:
                return c[0]
            except IndexError:
                return None
        else:
            return c

    def xpath(self, selector, first=False, _encoding=None):
        """Given an XPath selector, returns a list of :class:`Element <Element>` objects.

        If ``first`` is ``True``, only returns the first :class:`Element <Element>` found."""
        c = [Element(element=e, url=self.url, default_encoding=_encoding or self.encoding) for e in self.lxml.xpath(selector)]
        if first:
            try:
                return c[0]
            except IndexError:
                return None
        else:
            return c

    def search(self, template):
        """Searches the :class:`Element <Element>` for the given parse template."""
        return parse_search(template, self.html)

    def search_all(self, template):
        """Searches the :class:`Element <Element>` (multiple times) for the given parse
        template.
        """
        return [r for r in findall(template, self.html)]

    @property
    def links(self):
        """All found links on page, in as–is form."""
        def gen():
            for link in self.find('a'):

                try:
                    href = link.attrs['href'].strip()
                    if not href.startswith('#') and self.skip_anchors and href not in ['javascript:;']:
                        yield href
                except KeyError:
                    pass

        return set(g for g in gen())

    @property
    def absolute_links(self):
        """All found links on page, in absolute form."""
        def gen():
            for link in self.links:
                # Parse the link with stdlib.
                parsed = urlparse(link)._asdict()

                # Appears to be a relative link:
                if not parsed['netloc']:
                    parsed['netloc'] = urlparse(self.base_url).netloc
                if not parsed['scheme']:
                    parsed['scheme'] = urlparse(self.base_url).scheme

                # Re-construct URL, with new data.
                parsed = (v for v in parsed.values())
                href = urlunparse(parsed)

                yield href

        return set(g for g in gen())

    @property
    def base_url(self):
        """The base URL for the page. Supports the ``<base>`` tag."""

        # Support for <base> tag.
        base = self.find('base', first=True)
        if base:
            return base.attrs['href'].strip()

        else:
            url = '/'.join(self.url.split('/')[:-1])
            if url.endswith('/'):
                url = url[:-1]

            return url


class Element(BaseParser):
    """An element of HTML."""

    def __init__(self, *, element, url, default_encoding):
        super(Element, self).__init__(element=element, url=url, default_encoding=default_encoding)
        self.element = element

    def __repr__(self):
        attrs = []
        for attr in self.attrs:
            attrs.append('{}={}'.format(attr, repr(self.attrs[attr])))

        return "<Element {} {}>".format(repr(self.element.tag), ' '.join(attrs))

    @property
    def attrs(self):
        """Returns a dictionary of the attributes of the class:`Element <Element>`."""
        attrs = {k: self.pq.attr[k].strip() for k in self.element.keys()}

        # Split class up, as there are ussually many of them:
        if 'class' in attrs:
            attrs['class'] = tuple(attrs['class'].split())

        return attrs


class HTML(BaseParser):
    """An HTML document, ready for parsing."""

    def __init__(self, *, url, html, default_encoding=DEFAULT_ENCODING):
        super(HTML, self).__init__(
            element=PyQuery(html)('html'),
            html=html,
            url=url,
            default_encoding=default_encoding
        )

    def __repr__(self):
        return "<HTML url={}>".format(repr(self.url))


def user_agent(style=None):
    """Returns a random user-agent, if not requested one of a specific
    style.
    """

    if not style:
        return useragent.random
    else:
        return useragent[style]


class HTMLSession(requests.Session):
    """A consumable session, for cookie persistience and connection pooling,
    amongst other things.
    """

    def __init__(self, mock_browser=True, *args, **kwargs):
        super(HTMLSession, self).__init__(*args, **kwargs)

        # Mock a web browser's user agent.
        if mock_browser:
            self.headers['User-Agent'] = user_agent()

        self.hooks = {'response': self._handle_response}

    @staticmethod
    def _handle_response(response, **kwargs):
        """Requests HTTP Response handler. Attaches .html property to Response
        objects.
        """
        if not response.encoding:
            response.encoding = DEFAULT_ENCODING

        return response

    def request(self, *args, **kwargs):
        # Convert Request object into HTTPRequest object.
        r = super(HTMLSession, self).request(*args, **kwargs)
        html_r = HTMLResponse._from_response(r)

        return html_r


class BrowserHTMLSession(HTMLSession):
    """A web-browser interpreted session (for JavaScript), powered by
    PyQt5's QWebEngineView."""

    def __init__(self, *args, **kwargs):
        super(BrowserHTMLSession, self).__init__(*args, **kwargs)

    def request(self, *args, **kwargs):
        # Convert Request object into HTTPRequest object.
        r = super(BrowserHTMLSession, self).request(*args, **kwargs)

        r._content = self.render(r.text).encode(DEFAULT_ENCODING)
        r.encoding = DEFAULT_ENCODING

        return r

    @staticmethod
    def render(source_url):
        """Fully render HTML, JavaScript and all."""

        if 'QApplication' not in globals():
            raise RuntimeError('PyQt5 must be installed.')

        class Render(QWebEngineView):
            def __init__(self, html):
                self.html = None
                self.app = QApplication([])
                QWebEngineView.__init__(self)
                self.loadFinished.connect(self._loadFinished)
                self.setHtml(html)
                # self.load(QUrl(url))
                self.app.exec_()

            def _loadFinished(self, result):
                # This is an async call, you need to wait for this
                # to be called before closing the app
                self.page().toHtml(self._callable)

            def _callable(self, data):
                self.html = data
                # Data has been stored, it's safe to quit the app
                self.app.quit()

        return Render(source_url).html


# Backwards compatiblity.
session = HTMLSession()
Session = HTMLSession
BrowserSession = BrowserHTMLSession
