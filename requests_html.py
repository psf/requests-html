import sys
from urllib.parse import urlparse, urlunparse

import requests
from pyquery import PyQuery

from fake_useragent import UserAgent
from lxml import etree
from lxml.html.soupparser import fromstring
from parse import search as parse_search
from parse import findall

try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtWebEngineWidgets import QWebEngineView
except ImportError:
    pass


DEFAULT_ENCODING = 'utf-8'

useragent = UserAgent()


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
        if self._html:
            return self._html
        else:
            return etree.tostring(self.element).decode(self.encoding).strip()

    @html.setter
    def set_html(self, html):
        self._html = html

    @property
    def encoding(self):
        if self._encoding:
            return self._encoding

        # Scan meta tags for chaset.
        for meta_tag in self.find('meta', _encoding=self.default_encoding):

            # HTML 5 support.
            if 'charset' in meta_tag.attrs:
                self._encoding = meta_tag.attrs['charset']

            # HTML 4 support.
            if 'content' in meta_tag.attrs:
                try:
                    self._encoding = meta_tag.attrs['content'].split('charset=')[1]
                except IndexError:
                    pass

        return self._encoding if self._encoding else self.default_encoding

    @property
    def pq(self):
        """PyQuery representation of the element."""
        return PyQuery(self.element)

    @property
    def lxml(self):
        if self.element:
            return self.element
        else:
            return fromstring(self.html)

    @property
    def text(self):
        """The text content of the element."""
        return self.pq.text()

    @property
    def full_text(self):
        """The full text content (including links) of the element."""
        return self.lxml.text_content()

    def find(self, selector, first=False, _encoding=None):
        """Given a jQuery selector, returns a list of element objects."""
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
        """Given an XPath selector, returns a list of element objects."""
        c = [Element(element=e, url=self.url, default_encoding=_encoding or self.encoding) for e in self.lxml.xpath(selector)]
        if first:
            try:
                return c[0]
            except IndexError:
                return None
        else:
            return c

    def search(self, template):
        """Searches the element for the given parse template."""
        return parse_search(template, self.html)

    def search_all(self, template):
        """Searches the element (multiple times) for the given parse
        template.
        """
        return [r for r in findall(template, self.html)]

    @property
    def links(self):
        """All found links on page, in as–is form."""
        def gen():
            for link in self.find('a'):

                try:
                    href = link.attrs['href']
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
        """The base URL for the page."""

        # Support for <base> tag.
        base = self.find('base', first=True)
        if base:
            return base.attrs['href']

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
        """Returns a dictionary of the attributes of the element."""
        attrs = {k: self.pq.attr[k] for k in self.element.keys()}

        # Split class up, as there are ussually many of them:
        if 'class' in attrs:
            attrs['class'] = tuple(attrs['class'].split())

        return attrs


class HTML(BaseParser):
    """An HTML document."""

    def __init__(self, *, url, html, default_encoding=DEFAULT_ENCODING):
        super(HTML, self).__init__(
            element=fromstring(html),
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



class Session(requests.Session):
    """A consumable session, for cookie persistience and connection pooling,
    amongst other things.
    """

    def __init__(self, mock_browser=True, *args, **kwargs):
        super(Session, self).__init__(*args, **kwargs)

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

        response.html = HTML(url=response.url, html=response.text, default_encoding=response.encoding)

        return response


class BrowserSession(Session):
    """A web-browser interpreted session (for JavaScript)."""

    def __init__(self, *args, **kwargs):
        super(BrowserSession, self).__init__(*args, **kwargs)

    def request(self, *args, **kwargs):
        r = super(BrowserSession, self).request(*args, **kwargs)

        r._content = self.render(r.text).encode(DEFAULT_ENCODING)
        r.encoding = DEFAULT_ENCODING

        r.html = HTML(url=r.url, html=r.text, default_encoding=r.encoding)

        return r

    @staticmethod
    def render(source_url):
        """Fully render HTML, JavaScript and all."""

        if not 'QApplication' in globals():
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
session = Session()