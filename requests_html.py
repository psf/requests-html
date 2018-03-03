import sys
import asyncio
from urllib.parse import urlparse, urlunparse
from concurrent.futures._base import TimeoutError
from typing import Set, Union, List, MutableMapping, Optional

import pyppeteer
import requests
from pyquery import PyQuery
from pyquery.pyquery import fromstring

from fake_useragent import UserAgent
from lxml import etree
from lxml.html import HtmlElement
from lxml.html.soupparser import fromstring as soup_parse
from parse import search as parse_search
from parse import findall, Result
from w3lib.encoding import html_to_unicode

DEFAULT_ENCODING = 'utf-8'
DEFAULT_URL = 'https://example.org/'
DEFAULT_USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8'

useragent = None

# Typing.
_Find = Union[List['Element'], 'Element']
_XPath = Union[List[str], List['Element'], str, 'Element']
_Result = Union[List['Result'], 'Result']
_HTML = Union[str, bytes]
_BaseHTML = str
_UserAgent = str
_DefaultEncoding = str
_URL = str
_RawHTML = bytes
_Encoding = str
_LXML = HtmlElement
_Text = str
_Search = Result
_Links = Set[str]
_Attrs = MutableMapping

# Sanity checking.
try:
    assert sys.version_info.major == 3
    assert sys.version_info.minor > 5
except AssertionError:
    raise RuntimeError('Requests-HTML requires Python 3.6+!')


class BaseParser:
    """A basic HTML/Element Parser, for Humans.

    :param element: The element from which to base the parsing upon.
    :param default_encoding: Which encoding to default to.
    :param html: HTML from which to base the parsing upon (optional).
    :param url: The URL from which the HTML originated, used for ``absolute_links``.

    """

    def __init__(self, *, element, default_encoding: _DefaultEncoding = None, html: _HTML = None, url: _URL) -> None:
        self.element = element
        self.url = url
        self.skip_anchors = True
        self.default_encoding = default_encoding
        self._encoding = None
        self._html = html.encode(DEFAULT_ENCODING) if isinstance(html, str) else html
        self._lxml = None
        self._pq = None

    @property
    def raw_html(self) -> _RawHTML:
        """Bytes representation of the HTML content.
        (`learn more <http://www.diveintopython3.net/strings.html>`_).
        """
        if self._html:
            return self._html
        else:
            return etree.tostring(self.element, encoding='unicode').strip().encode(self.encoding)

    @property
    def html(self) -> _BaseHTML:
        """Unicode representation of the HTML content
        (`learn more <http://www.diveintopython3.net/strings.html>`_).
        """
        if self._html:
            return self.raw_html.decode(self.encoding)
        else:
            return etree.tostring(self.element, encoding='unicode').strip()

    @html.setter
    def html(self, html: bytes) -> None:
        """Property setter for self.html."""
        self._html = html

    @property
    def encoding(self) -> _Encoding:
        """The encoding string to be used, extracted from the HTML and
        :class:`HTMLResponse <HTMLResponse>` headers.
        """
        if self._encoding:
            return self._encoding

        # Scan meta tags for charset.
        if self._html:
            self._encoding = html_to_unicode(self.default_encoding, self._html)[0]

        return self._encoding if self._encoding else self.default_encoding

    @encoding.setter
    def encoding(self, enc: str) -> None:
        """Property setter for self.encoding."""
        self._encoding = enc

    @property
    def pq(self) -> PyQuery:
        """`PyQuery <https://pythonhosted.org/pyquery/>`_ representation
        of the :class:`Element <Element>` or :class:`HTML <HTML>`.
        """
        if self._pq is None:
            self._pq = PyQuery(self.html)

        return self._pq

    @property
    def lxml(self) -> HtmlElement:
        """`lxml <http://lxml.de>`_ representation of the
        :class:`Element <Element>` or :class:`HTML <HTML>`.
        """
        if self._lxml is None:
            self._lxml = soup_parse(self.html, features='html.parser')

        return self._lxml

    @property
    def text(self) -> _Text:
        """The text content of the
        :class:`Element <Element>` or :class:`HTML <HTML>`.
        """
        return self.pq.text()

    @property
    def full_text(self) -> _Text:
        """The full text content (including links) of the
        :class:`Element <Element>` or :class:`HTML <HTML>`.
        """
        return self.lxml.text_content()

    def find(self, selector: str, first: bool = False, _encoding: str = None) -> _Find:
        """Given a CSS Selector, returns a list of
        :class:`Element <Element>` objects or a single one.

        :param selector: CSS Selector to use.
        :param first: Whether or not to return just the first result.
        :param _encoding: The encoding format.

        Example CSS Selectors:

        - ``a``
        - ``a.someClass``
        - ``a#someID``
        - ``a[target=_blank]``

        See W3School's `CSS Selectors Reference
        <https://www.w3schools.com/cssref/css_selectors.asp>`_
        for more details.

        If ``first`` is ``True``, only returns the first
        :class:`Element <Element>` found.
        """

        encoding = _encoding or self.encoding
        elements = [
            Element(element=found, url=self.url, default_encoding=encoding)
            for found in self.pq(selector)
        ]

        return _get_first_or_list(elements, first)

    def xpath(self, selector: str, first: bool = False, _encoding: str = None) -> _XPath:
        """Given an XPath selector, returns a list of
        :class:`Element <Element>` objects or a single one.

        :param selector: XPath Selector to use.
        :param first: Whether or not to return just the first result.
        :param _encoding: The encoding format.

        If a sub-selector is specified (e.g. ``//a/@href``), a simple
        list of results is returned.

        See W3School's `XPath Examples
        <https://www.w3schools.com/xml/xpath_examples.asp>`_
        for more details.

        If ``first`` is ``True``, only returns the first
        :class:`Element <Element>` found.
        """
        selected = self.lxml.xpath(selector)

        elements = [
            Element(element=selection, url=self.url, default_encoding=_encoding or self.encoding)
            if not isinstance(selection, etree._ElementUnicodeResult) else str(selection)
            for selection in selected
        ]

        return _get_first_or_list(elements, first)

    def search(self, template: str) -> Result:
        """Search the :class:`Element <Element>` for the given Parse template.

        :param template: The Parse template to use.
        """

        return parse_search(template, self.html)

    def search_all(self, template: str) -> _Result:
        """Search the :class:`Element <Element>` (multiple times) for the given parse
        template.

        :param template: The Parse template to use.
        """
        return [r for r in findall(template, self.html)]

    @property
    def links(self) -> _Links:
        """All found links on page, in as–is form."""

        def gen():
            for link in self.find('a'):

                try:
                    href = link.attrs['href'].strip()
                    if href and not (href.startswith('#') and self.skip_anchors) and not href.startswith('javascript:'):
                        yield href
                except KeyError:
                    pass

        return set(gen())

    @property
    def absolute_links(self) -> _Links:
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
    def base_url(self) -> _URL:
        """The base URL for the page. Supports the ``<base>`` tag
        (`learn more <https://www.w3schools.com/tags/tag_base.asp>`_)."""

        # Support for <base> tag.
        base = self.find('base', first=True)
        if base:
            return base.attrs['href'].strip()

        url = '/'.join(self.url.split('/')[:-1])
        if url.endswith('/'):
            url = url[:-1]

        return url


class Element(BaseParser):
    """An element of HTML.

    :param element: The element from which to base the parsing upon.
    :param url: The URL from which the HTML originated, used for ``absolute_links``.
    :param default_encoding: Which encoding to default to.
    """

    def __init__(self, *, element, url: _URL, default_encoding: _DefaultEncoding = None) -> None:
        super(Element, self).__init__(element=element, url=url, default_encoding=default_encoding)
        self.element = element

    def __repr__(self) -> str:
        attrs = ['{}={}'.format(attr, repr(self.attrs[attr])) for attr in self.attrs]
        return "<Element {} {}>".format(repr(self.element.tag), ' '.join(attrs))

    @property
    def attrs(self) -> _Attrs:
        """Returns a dictionary of the attributes of the :class:`Element <Element>`
        (`learn more <https://www.w3schools.com/tags/ref_attributes.asp>`_).
        """
        attrs = {k: v for k, v in self.element.items()}

        # Split class up, as there are ussually many of them:
        if 'class' in attrs:
            attrs['class'] = tuple(attrs['class'].split())

        return attrs


class HTML(BaseParser):
    """An HTML document, ready for parsing.

    :param url: The URL from which the HTML originated, used for ``absolute_links``.
    :param html: HTML from which to base the parsing upon (optional).
    :param default_encoding: Which encoding to default to.
    """

    def __init__(self, *, url: str = DEFAULT_URL, html: _HTML, default_encoding: str = DEFAULT_ENCODING) -> None:

        # Convert incoming unicode HTML into bytes.
        if isinstance(html, str):
            html = html.encode(DEFAULT_ENCODING)

        super(HTML, self).__init__(
            # Convert unicode HTML to bytes.
            element=PyQuery(html)('html') or PyQuery(f'<html>{html}</html>')('html'),
            html=html,
            url=url,
            default_encoding=default_encoding
        )

    def __repr__(self) -> str:
        return f"<HTML url={self.url!r}>"

    def render(self, retries: int = 8, script: str = None, wait: float = 0.2, scrolldown=False, sleep: int = 0, reload: bool = True, timeout: Union[float, int] = 8.0):
        """Reloads the response in Chromium, and replaces HTML content
        with an updated version, with JavaScript executed.

        :param retries: The number of times to retry loading the page in Chromium.
        :param script: JavaScript to execute upon page load (optional).
        :param wait: The number of seconds to wait before loading the page, preventing timeouts (optional).
        :param scrolldown: Integer, if provided, of how many times to page down.
        :param sleep: Integer, if provided, of how many long to sleep after initial render.
        :param reload: If ``False``, content will not be loaded from the browser, but will be provided from memory.

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
        async def _async_render(*, url: str, script: str = None, scrolldown, sleep: int, wait: float, reload, content: Optional[str], timeout: Union[float, int]):
            try:
                browser = pyppeteer.launch(headless=True)
                page = await browser.newPage()

                # Wait before rendering the page, to prevent timeouts.
                await asyncio.sleep(wait)

                # Load the given page (GET request, obviously.)
                if reload:
                    await page.goto(url, options={'timeout': int(timeout * 1000)})
                else:
                    await page.goto(f'data:text/html,{self.html}', options={'timeout': int(timeout * 1000)})

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

        # Automatically set Reload to False, if example URL is being used.
        if self.url == DEFAULT_URL:
            reload = False

        for i in range(retries):
            if not content:
                try:

                    content, result = loop.run_until_complete(_async_render(url=self.url, script=script, sleep=sleep, wait=wait, content=self.html, reload=reload, scrolldown=scrolldown, timeout=timeout))
                except TimeoutError:
                    pass

        html = HTML(url=self.url, html=content.encode(DEFAULT_ENCODING), default_encoding=DEFAULT_ENCODING)
        self.__dict__.update(html.__dict__)
        return result


class HTMLResponse(requests.Response):
    """An HTML-enabled :class:`requests.Response <requests.Response>` object.
    Effectively the same, but with an intelligent ``.html`` property added.
    """

    def __init__(self) -> None:
        super(HTMLResponse, self).__init__()
        self._html = None  # type: HTML

    @property
    def html(self) -> HTML:
        if not self._html:
            self._html = HTML(url=self.url, html=self.content, default_encoding=self.encoding)

        return self._html

    @classmethod
    def _from_response(cls, response):
        html_r = cls()
        html_r.__dict__.update(response.__dict__)
        return html_r


def user_agent(style=None) -> _UserAgent:
    """Returns an apparently legit user-agent, if not requested one of a specific
    style. Defaults to a Chrome-style User-Agent.
    """
    global useragent
    if (not useragent) and style:
        useragent = UserAgent()

    return useragent[style] if style else DEFAULT_USER_AGENT


def _get_first_or_list(l, first=False):
    if first:
        try:
            return l[0]
        except IndexError:
            return None
    else:
        return l


class HTMLSession(requests.Session):
    """A consumable session, for cookie persistence and connection pooling,
    amongst other things.
    """

    def __init__(self, mock_browser=True):
        super(HTMLSession, self).__init__()

        # Mock a web browser's user agent.
        if mock_browser:
            self.headers['User-Agent'] = user_agent()

        self.hooks = {'response': self._handle_response}

    @staticmethod
    def _handle_response(response, **kwargs) -> HTMLResponse:
        """Requests HTTP Response handler. Attaches .html property to
        class:`requests.Response <requests.Response>` objects.
        """
        if not response.encoding:
            response.encoding = DEFAULT_ENCODING

        return response

    def request(self, *args, **kwargs) -> HTMLResponse:
        """Makes an HTTP Request, with mocked User–Agent headers.
        Returns a class:`HTTPResponse <HTTPResponse>`.
        """
        # Convert Request object into HTTPRequest object.
        r = super(HTMLSession, self).request(*args, **kwargs)

        return HTMLResponse._from_response(r)
