import asyncio
from urllib.parse import urlparse, urlunparse
from concurrent.futures._base import TimeoutError
from typing import Set

import pyppeteer
import requests
from pyquery import PyQuery

from fake_useragent import UserAgent
from lxml import etree
from lxml.html import HtmlElement
from lxml.html.soupparser import fromstring
from parse import search as parse_search
from parse import findall, Result
from w3lib.encoding import html_to_unicode


DEFAULT_ENCODING = 'utf-8'
DEFAULT_URL = 'https://example.org/'

useragent = UserAgent()



class BaseParser:
    """A basic HTML/Element Parser, for Humans."""

    def __init__(self, *, element, default_encoding: str = None, html: str = None, url: str) -> None:
        self.element = element
        self.url = url
        self.skip_anchors = True
        self.default_encoding = default_encoding
        self._encoding = None
        self._html = html

    @property
    def raw_html(self) -> bytes:
        """Bytes representation of the HTML content (`learn more <http://www.diveintopython3.net/strings.html>`_)."""
        if self._html:
            return self._html
        else:
            return etree.tostring(self.element, encoding='unicode').strip().encode(self.encoding)

    @property
    def html(self) -> str:
        """Unicode representation of the HTML content (`learn more <http://www.diveintopython3.net/strings.html>`_)."""
        if self._html:
            return self._html.decode(self.encoding)
        else:
            return etree.tostring(self.element, encoding='unicode').strip()

    @html.setter
    def set_html(self, html: bytes) -> None:
        """Property setter for self.html."""
        self._html = html

    @property
    def encoding(self) -> str:
        """The encoding string to be used, extracted from the HTML and
        :class:`HTMLResponse <HTMLResponse>` headers.
        """
        if self._encoding:
            return self._encoding

        # Scan meta tags for chaset.
        if self._html:
            self._encoding = html_to_unicode(self.default_encoding, self._html)[0]

        return self._encoding if self._encoding else self.default_encoding

    @property
    def pq(self) -> PyQuery:
        """`PyQuery <https://pythonhosted.org/pyquery/>`_ representation
        of the :class:`Element <Element>` or :class:`HTML <HTML>`.
        """
        return PyQuery(self.element)

    @property
    def lxml(self) -> HtmlElement:
        """`lxml <http://lxml.de>`_ representation of the
        :class:`Element <Element>` or :class:`HTML <HTML>`.
        """
        return fromstring(self.html)

    @property
    def text(self) -> str:
        """The text content of the :class:`Element <Element>` or :class:`HTML <HTML>`."""
        return self.pq.text()

    @property
    def full_text(self) -> str:
        """The full text content (including links) of the :class:`Element <Element>` or :class:`HTML <HTML>`.."""
        return self.lxml.text_content()

    def find(self, selector: str, first: bool = False, _encoding: str = None):
        """Given a CSS Selector, returns a list of :class:`Element <Element>` objects.

        Example CSS Selectors:

        - ``a``
        - ``a.someClass``
        - ``a#someID``
        - ``a[target=_blank]``

        See W3School's `CSS Selectors Reference <https://www.w3schools.com/cssref/css_selectors.asp>`_ for more details.

        If ``first`` is ``True``, only returns the first :class:`Element <Element>` found."""

        encoding = _encoding or self.encoding
        elements = [
            Element(element=found, url=self.url, default_encoding=encoding)
            for found in self.pq(selector)
        ]

        if first:
            try:
                return elements[0]
            except IndexError:
                return None
        else:
            return elements

    def xpath(self, selector: str, first: bool = False, _encoding: str = None):
        """Given an XPath selector, returns a list of
        :class:`Element <Element>` objects.

        If a sub-selector is specified (e.g. ``//a/@href``), a simple
        list of results is returned.

        See W3School's `XPath Examples
        <https://www.w3schools.com/xml/xpath_examples.asp>`_
        for more details.

        If ``first`` is ``True``, only returns the first
        :class:`Element <Element>` found.
        """
        selected = self.lxml.xpath(selector)
        c = []
        for selection in selected:
            if not isinstance(selection, etree._ElementUnicodeResult):
                element = Element(element=selection, url=self.url, default_encoding=_encoding or self.encoding)
            else:
                element = selection
            c.append(element)

        if first:
            try:
                return c[0]
            except IndexError:
                return None
        else:
            return c

    def search(self, template: str) -> Result:
        """Searches the :class:`Element <Element>` for the given parse template."""
        return parse_search(template, self.html)

    def search_all(self, template: str) -> Result:
        """Searches the :class:`Element <Element>` (multiple times) for the given parse
        template.
        """
        return [r for r in findall(template, self.html)]

    @property
    def links(self) -> Set[str]:
        """All found links on page, in as–is form."""
        def gen():
            for link in self.find('a'):

                try:
                    href = link.attrs['href'].strip()
                    if not(href.startswith('#') and self.skip_anchors) and href not in ['javascript:;']:
                        if href:
                            yield href
                except KeyError:
                    pass

        return set(gen())

    @property
    def absolute_links(self) -> Set[str]:
        """All found links on page, in absolute form
        (`learn more <https://www.navegabem.com/absolute-or-relative-links.html>`_).
        """
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

        return set(gen())

    @property
    def base_url(self) -> str:
        """The base URL for the page. Supports the ``<base>`` tag
        (`learn more <https://www.w3schools.com/tags/tag_base.asp>`_)."""

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

    def __init__(self, *, element, url, default_encoding) -> None:
        super(Element, self).__init__(element=element, url=url, default_encoding=default_encoding)
        self.element = element

    def __repr__(self) -> str:
        attrs = []
        for attr in self.attrs:
            attrs.append('{}={}'.format(attr, repr(self.attrs[attr])))

        return "<Element {} {}>".format(repr(self.element.tag), ' '.join(attrs))

    @property
    def attrs(self) -> dict:
        """Returns a dictionary of the attributes of the :class:`Element <Element>`
        (`learn more <https://www.w3schools.com/tags/ref_attributes.asp>`_).
        """
        attrs = {k: self.pq.attr[k].strip() for k in self.element.keys()}

        # Split class up, as there are ussually many of them:
        if 'class' in attrs:
            attrs['class'] = tuple(attrs['class'].split())

        return attrs


class HTML(BaseParser):
    """An HTML document, ready for parsing."""

    def __init__(self, *, url=DEFAULT_URL, html, default_encoding=DEFAULT_ENCODING) -> None:

        # Convert incoming unicode HTML into bytes.
        if isinstance(html, str):
            html = html.encode(DEFAULT_ENCODING)

        super(HTML, self).__init__(
            # Convert unicode HTML to bytes.
            element=PyQuery(html)('html') or PyQuery('<html>{}</html>'.format(html))('html'),
            html=html,
            url=url,
            default_encoding=default_encoding
        )

    def __repr__(self) -> str:
        return "<HTML url={}>".format(repr(self.url))

    def render(self, retries: int = 8, script: str = None, scrolldown=False, sleep: int = 0):
        """Reloads the response in Chromium, and replaces HTML content
        with an updated version, with JavaScript executed.

        If ``scrolldown`` is specified, the page will scrolldown the specified
        number of times, after sleeping the specified amount of time
        (e.g. ``scrolldown=10, sleep=1``).

        If just ``sleep`` is provided, the rendering will wait *n* seconds, before
        returning.

        If ``script`` is specified, it will execute the provided JavaScript at
        runtime. Example:

        .. code-block:: python

            script = \"\"\"
                () => {
                    return {
                        width: document.documentElement.clientWidth,
                        height: document.documentElement.clientHeight,
                        deviceScaleFactor: window.devicePixelRatio,
                    }
                }
            \"\"\"

        Returns the return value of the executed  ``script``, if any is provided:

        .. code-block:: python

            >>> r.html.render(script=script)
            {'width': 800, 'height': 600, 'deviceScaleFactor': 1}

        Warning: the first time you run this method, it will download
        Chromium into your home directory (``~/.pyppeteer``).
        """
        async def _async_render(*, url: str, script: str = None, scrolldown, sleep: int):
            try:
                browser = pyppeteer.launch(headless=True)
                page = await browser.newPage()

                # Load the given page (GET request, obviously.)
                await page.goto(url)

                result = None
                if script:
                    result = await page.evaluate(script)

                if scrolldown:
                    for _ in range(scrolldown):
                        await page._keyboard.down('PageDown')
                        await asyncio.sleep(sleep)
                else:
                    await asyncio.sleep(sleep)

                if scrolldown:
                    await page._keyboard.up('PageDown')

                # Return the content of the page, JavaScript evaluated.
                content = await page.content()
                return content, result
            except TimeoutError:
                return None

        loop = asyncio.get_event_loop()
        content = None

        for i in range(retries):
            if not content:
                try:
                    content, result = loop.run_until_complete(_async_render(url=self.url, script=script, sleep=sleep, scrolldown=scrolldown))
                except TimeoutError:
                    pass

        html = HTML(url=self.url, html=content.encode(DEFAULT_ENCODING), default_encoding=DEFAULT_ENCODING)
        self.__dict__.update(html.__dict__)
        return result


class HTMLResponse(requests.Response):
    """An HTML-enabled :class:`Response <Response>` object.
    Same as Requests class:`Response <Response>` object, but with an
    intelligent ``.html`` property added.
    """

    def __init__(self, *args, **kwargs) -> None:
        super(HTMLResponse, self).__init__(*args, **kwargs)
        self._html = None

    @property
    def html(self) -> HTML:
        if self._html:
            return self._html

        self._html = HTML(url=self.url, html=self.content, default_encoding=self.encoding)
        return self._html

    @classmethod
    def _from_response(cls, response):
        html_r = cls()
        html_r.__dict__.update(response.__dict__)
        return html_r


def user_agent(style='chrome') -> str:
    """Returns a random user-agent, if not requested one of a specific
    style. Defaults to a Chrome-style User-Agent.
    """

    if not style:
        return useragent.random
    else:
        return useragent[style]


class HTMLSession(requests.Session):
    """A consumable session, for cookie persistence and connection pooling,
    amongst other things.
    """

    def __init__(self, mock_browser=True, *args, **kwargs):
        super(HTMLSession, self).__init__(*args, **kwargs)

        # Mock a web browser's user agent.
        if mock_browser:
            self.headers['User-Agent'] = user_agent()

        self.hooks = {'response': self._handle_response}

    @staticmethod
    def _handle_response(response, **kwargs) -> HTMLResponse:
        """Requests HTTP Response handler. Attaches .html property to Response
        objects.
        """
        if not response.encoding:
            response.encoding = DEFAULT_ENCODING

        return response

    def request(self, *args, **kwargs) -> HTMLResponse:
        # Convert Request object into HTTPRequest object.
        r = super(HTMLSession, self).request(*args, **kwargs)
        html_r = HTMLResponse._from_response(r)

        return html_r
