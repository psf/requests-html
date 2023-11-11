import asyncio
import http.cookiejar
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures._base import TimeoutError
from functools import partial, wraps
from typing import Any, Optional, Union
from urllib.parse import urljoin, urlparse, urlunparse

import lxml
import requests
from fake_useragent import UserAgent  # type: ignore
from lxml import etree
from lxml.html import HtmlElement
from lxml.html import tostring as lxml_html_tostring
from lxml.html.clean import Cleaner
from lxml.html.soupparser import fromstring as soup_parse
from parse import Result, findall  # type: ignore
from parse import search as parse_search  # type: ignore
from playwright._impl._api_structures import SetCookieParam
from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright
from pyquery import PyQuery  # type: ignore
from w3lib.encoding import html_to_unicode

DEFAULT_ENCODING = "utf-8"
DEFAULT_URL = "https://example.org/"
DEFAULT_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
DEFAULT_NEXT_SYMBOL = ["next", "more", "older"]

cleaner = Cleaner()
cleaner.javascript = True
cleaner.style = True

# Typing.
_Find = Union[list["Element"], "Element"]
_XPath = Union[list[str], list["Element"], str, "Element"]
_Result = Union[list[Result], Result]
_HTML = Optional[Union[str, bytes]]
_BaseHTML = str
_UserAgent = str
_DefaultEncoding = Optional[str]
_Encoding = Optional[str]
_URL = str
_RawHTML = bytes
_LXML = Optional[HtmlElement]
_Text = str
_Containing = Optional[Union[str, list[str]]]
_Links = set[str]
_Attrs = dict
_Next = Optional[Union["HTML", list[str], requests.Response]]
_NextSymbol = Optional[list[str]]
_Session = Union["HTMLSession", "AsyncHTMLSession"]

# Sanity checking.
try:
    assert sys.version_info.major == 3
    assert sys.version_info.minor > 8
except AssertionError:
    raise RuntimeError("Requests-HTML requires Python 3.9+!")

# install browsers
os.system("playwright install")


class Retry:
    def __init__(self, tries: int = 3, backoff_base: int = 2) -> None:
        self.tries = tries
        self.backoff_base = backoff_base

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(self.tries):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    pass
                time.sleep(self.backoff_base ** (i + 1))
            raise RuntimeError("Unable to render the page. Try increasing timeout")

        return wrapper


class BaseParser:
    """A basic HTML/Element Parser, for Humans.

    :param element: The element from which to base the parsing upon.
    :param default_encoding: Which encoding to default to.
    :param html: HTML from which to base the parsing upon (optional).
    :param url: The URL from which the HTML originated, used for ``absolute_links``.

    """

    def __init__(
        self,
        *,
        element,
        default_encoding: _DefaultEncoding = None,
        html: _HTML = None,
        url: _URL,
    ) -> None:
        self.element = element
        self.url = url
        self.skip_anchors = True
        self.default_encoding = default_encoding
        self._encoding: _Encoding = None
        self._html = html.encode(DEFAULT_ENCODING) if isinstance(html, str) else html
        self._lxml: _LXML = None
        self._pq = None

    @property
    def raw_html(self) -> _RawHTML:
        """Bytes representation of the HTML content.
        (`learn more <http://www.diveintopython3.net/strings.html>`_).
        """
        if self._html:
            return self._html
        else:
            return (
                etree.tostring(self.element, encoding="unicode")
                .strip()
                .encode(self.encoding if self.encoding is not None else "")
            )

    @raw_html.setter
    def raw_html(self, html: bytes) -> None:
        """Property setter for self.html."""
        self._html = html

    @property
    def html(self) -> _BaseHTML:
        """Unicode representation of the HTML content
        (`learn more <http://www.diveintopython3.net/strings.html>`_).
        """
        if self._html:
            return self.raw_html.decode(
                self.encoding if self.encoding is not None else "", errors="replace"
            )
        else:
            return etree.tostring(self.element, encoding="unicode").strip()

    @html.setter
    def html(self, html: str) -> None:
        self._html = html.encode(self.encoding if self.encoding is not None else "")

    @property
    def encoding(self) -> _Encoding:
        """The encoding string to be used, extracted from the HTML and
        :class:`HTMLResponse <HTMLResponse>` headers.
        """
        if self._encoding is not None:
            return self._encoding

        # Scan meta tags for charset.
        if self._html:
            self._encoding = html_to_unicode(self.default_encoding, self._html)[0]
            # Fall back to requests' detected encoding if decode fails.
            try:
                self.raw_html.decode(
                    self.encoding if self.encoding is not None else "", errors="replace"
                )
            except UnicodeDecodeError:
                self._encoding = self.default_encoding

        return self._encoding if self._encoding is not None else self.default_encoding

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
            self._pq = PyQuery(self.lxml)

        return self._pq

    @property
    def lxml(self) -> HtmlElement:
        """`lxml <http://lxml.de>`_ representation of the
        :class:`Element <Element>` or :class:`HTML <HTML>`.
        """
        if self._lxml is None:
            try:
                self._lxml = soup_parse(self.html, features="html.parser")
            except ValueError:
                self._lxml = lxml.html.fromstring(self.raw_html)

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

    def find(
        self,
        selector: str = "*",
        *,
        containing: _Containing = None,
        clean: bool = False,
        first: bool = False,
        _encoding: str = "",
    ) -> _Find:
        """Given a CSS Selector, returns a list of
        :class:`Element <Element>` objects or a single one.

        :param selector: CSS Selector to use.
        :param clean: Whether or not to sanitize the found HTML of ``<script>`` and ``<style>`` tags.
        :param containing: If specified, only return elements that contain the provided text.
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

        # Convert a single containing into a list.
        if isinstance(containing, str):
            containing = [containing]

        encoding = _encoding or self.encoding
        elements = [
            Element(element=found, url=self.url, default_encoding=encoding)
            for found in self.pq(selector)
        ]

        if containing:
            elements_copy = elements.copy()
            elements = []

            for element in elements_copy:
                if any([c.lower() in element.full_text.lower() for c in containing]):
                    elements.append(element)

            elements.reverse()

        # Sanitize the found HTML.
        if clean:
            elements_copy = elements.copy()
            elements = []

            for element in elements_copy:
                element.raw_html = lxml_html_tostring(cleaner.clean_html(element.lxml))
                elements.append(element)

        return _get_first_or_list(elements, first)

    def xpath(
        self,
        selector: str,
        *,
        clean: bool = False,
        first: bool = False,
        _encoding: str = "",
    ) -> _XPath:
        """Given an XPath selector, returns a list of
        :class:`Element <Element>` objects or a single one.

        :param selector: XPath Selector to use.
        :param clean: Whether or not to sanitize the found HTML of ``<script>`` and ``<style>`` tags.
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
            Element(
                element=selection,
                url=self.url,
                default_encoding=_encoding or self.encoding,
            )
            if not isinstance(selection, etree._ElementUnicodeResult)
            else str(selection)
            for selection in selected
        ]

        # Sanitize the found HTML.
        if clean:
            elements_copy = elements.copy()
            elements = []

            for element in elements_copy:
                if isinstance(element, Element):
                    element.raw_html = lxml_html_tostring(
                        cleaner.clean_html(element.lxml)
                    )
                elements.append(element)

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
            for link in self.find("a"):
                try:
                    href = link.attrs["href"].strip()
                    if (
                        href
                        and not (href.startswith("#") and self.skip_anchors)
                        and not href.startswith(("javascript:", "mailto:"))
                    ):
                        yield href
                except KeyError:
                    pass

        return set(gen())

    def _make_absolute(self, link):
        """Makes a given link absolute."""

        # Parse the link with stdlib.
        parsed = urlparse(link)._asdict()

        # If link is relative, then join it with base_url.
        if not parsed["netloc"]:
            return urljoin(self.base_url, link)

        # Link is absolute; if it lacks a scheme, add one from base_url.
        if not parsed["scheme"]:
            parsed["scheme"] = urlparse(self.base_url).scheme

            # Reconstruct the URL to incorporate the new scheme.
            parsed = (v for v in parsed.values())
            return urlunparse(parsed)

        # Link is absolute and complete with scheme; nothing to be done here.
        return link

    @property
    def absolute_links(self) -> _Links:
        """All found links on page, in absolute form
        (`learn more <https://www.navegabem.com/absolute-or-relative-links.html>`_).
        """

        def gen():
            for link in self.links:
                yield self._make_absolute(link)

        return set(gen())

    @property
    def base_url(self) -> _URL:
        """The base URL for the page. Supports the ``<base>`` tag
        (`learn more <https://www.w3schools.com/tags/tag_base.asp>`_)."""

        # Support for <base> tag.
        base = self.find("base", first=True)
        if base and isinstance(base, Element):
            result = base.attrs.get("href", "").strip()
            if result:
                return result

        # Parse the url to separate out the path
        parsed = urlparse(self.url)._asdict()

        # Remove any part of the path after the last '/'
        parsed["path"] = "/".join(parsed["path"].split("/")[:-1]) + "/"

        # Reconstruct the url with the modified path
        return urlunparse(tuple(v for v in parsed.values()))


class Element(BaseParser):
    """An element of HTML.

    :param element: The element from which to base the parsing upon.
    :param url: The URL from which the HTML originated, used for ``absolute_links``.
    :param default_encoding: Which encoding to default to.
    """

    def __init__(
        self, *, element, url: _URL, default_encoding: _DefaultEncoding = None
    ) -> None:
        super(Element, self).__init__(
            element=element, url=url, default_encoding=default_encoding
        )
        self.element = element
        self.tag = element.tag
        self.lineno = element.sourceline
        self._attrs: _Attrs = {}

    def __repr__(self) -> str:
        attrs = ["{}={}".format(attr, repr(self.attrs[attr])) for attr in self.attrs]
        return "<Element {} {}>".format(repr(self.element.tag), " ".join(attrs))

    @property
    def attrs(self) -> _Attrs:
        """Returns a dictionary of the attributes of the :class:`Element <Element>`
        (`learn more <https://www.w3schools.com/tags/ref_attributes.asp>`_).
        """
        if not self._attrs:
            self._attrs = {k: v for k, v in self.element.items()}

            # Split class and rel up, as there are usually many of them:
            for attr in ["class", "rel"]:
                if attr in self._attrs:
                    self._attrs[attr] = tuple(self._attrs[attr].split())

        return self._attrs


class HTML(BaseParser):
    """An HTML document, ready for parsing.

    :param url: The URL from which the HTML originated, used for ``absolute_links``.
    :param html: HTML from which to base the parsing upon (optional).
    :param default_encoding: Which encoding to default to.
    """

    def __init__(
        self,
        *,
        session: Optional[_Session] = None,
        url: str = DEFAULT_URL,
        html: _HTML,
        default_encoding: _DefaultEncoding = DEFAULT_ENCODING,
        async_: bool = False,
    ) -> None:
        # Convert incoming unicode HTML into bytes.
        if isinstance(html, str):
            html = html.encode(DEFAULT_ENCODING)

        pq = PyQuery(html)
        super(HTML, self).__init__(
            element=pq("html") or pq.wrapAll("<html></html>")("html"),
            html=html,
            url=url,
            default_encoding=default_encoding,
        )
        self.session = session or async_ and AsyncHTMLSession() or HTMLSession()
        self.page = None
        self.next_symbol = DEFAULT_NEXT_SYMBOL

    def __repr__(self) -> str:
        return f"<HTML url={self.url!r}>"

    def next(self, fetch: bool = False, next_symbol: _NextSymbol = None) -> _Next:
        """Attempts to find the next page, if there is one. If ``fetch``
        is ``True`` (default), returns :class:`HTML <HTML>` object of
        next page. If ``fetch`` is ``False``, simply returns the next URL.

        """
        if next_symbol is None:
            next_symbol = DEFAULT_NEXT_SYMBOL

        def get_next():
            candidates = self.find("a", containing=next_symbol)

            for candidate in candidates:
                if candidate.attrs.get("href"):
                    # Support 'next' rel (e.g. reddit).
                    if "next" in candidate.attrs.get("rel", []):
                        return candidate.attrs["href"]

                    # Support 'next' in classnames.
                    for _class in candidate.attrs.get("class", []):
                        if "next" in _class:
                            return candidate.attrs["href"]

                    if "page" in candidate.attrs["href"]:
                        return candidate.attrs["href"]

            return candidates[-1].attrs["href"] if candidates else None

        __next = get_next()
        if __next:
            url = self._make_absolute(__next)
        else:
            return None

        if fetch:
            return self.session.get(url)
        else:
            return url

    def __iter__(self):
        next = self

        while True:
            yield next
            try:
                next = next.next(fetch=True, next_symbol=self.next_symbol).html
            except AttributeError:
                break

    def __next__(self):
        return self.next(fetch=True, next_symbol=self.next_symbol).html

    def __aiter__(self):
        return self

    async def __anext__(self):
        while True:
            url = self.next(fetch=False, next_symbol=self.next_symbol)
            if not url:
                break
            response = await self.session.get(url)
            return response.html

    @Retry()
    def _render(
        self,
        *,
        url: str,
        script: Optional[str] = None,
        content: Optional[str],
        keep_page: bool,
        cookies: Optional[list[SetCookieParam]] = None,
        render_html: bool = False,
    ) -> tuple[Optional[str], Optional[Any], Optional[Any]]:
        try:
            context = self.browser.new_context()
            if cookies is not None:
                context.add_cookies(cookies)
            page = context.new_page()
            if render_html:
                page.goto(f"data:text/html,{self.html}")
            else:
                page.goto(url)

            result = None
            if script is not None:
                result = page.evaluate(script)

            content = page.content()
            if not keep_page:
                page.close()
                page = None
            context.close()
            return content, result, page
        except TimeoutError:
            page.close()
            return None, None, None

    @Retry()
    async def _async_render(
        self,
        *,
        url: str,
        script: Optional[str] = None,
        content: Optional[str],
        keep_page: bool,
        cookies: Optional[list[SetCookieParam]] = None,
        render_html: bool = False,
    ) -> tuple[Optional[str], Optional[Any], Optional[Any]]:
        """Handle page creation and js rendering. Internal use for arender methods."""
        try:
            context = await self.browser.new_context()
            if cookies is not None:
                await context.add_cookies(cookies)
            page = await context.new_page()
            if render_html:
                await page.goto(f"data:text/html,{self.html}")
            else:
                await page.goto(url)

            result = None
            if script is not None:
                result = await page.evaluate(script)

            content = await page.content()
            if not keep_page:
                await page.close()
                page = None
            await context.close()
            return content, result, page
        except TimeoutError:
            await page.close()
            return None, None, None

    def _convert_cookiejar_to_render(
        self, session_cookiejar: http.cookiejar.CookieJar
    ) -> SetCookieParam:
        """
        Convert HTMLSession.cookies:cookiejar[] for SetCookieParam
        """
        cookie_render: SetCookieParam = {}

        def __convert(cookiejar: http.cookiejar.CookieJar, key: str):
            v = getattr(cookiejar, key, None)
            return "" if v is None else {key: v}

        for key in SetCookieParam.__annotations__:
            cookie_render.update(__convert(session_cookiejar, key))
        return cookie_render

    def _convert_cookiesjar_to_render(self):
        """
        Convert HTMLSession.cookies for browser.newPage().setCookie
        Return a list of dict
        """
        cookies_render = []
        if isinstance(self.session.cookies, http.cookiejar.CookieJar):
            for cookie in self.session.cookies:
                cookies_render.append(self._convert_cookiejar_to_render(cookie))
        return cookies_render

    def render(
        self,
        script: Optional[str] = None,
        keep_page: bool = False,
        cookies: Optional[list] = None,
        send_cookies_session: bool = False,
        render_html: bool = False,
    ):
        """Reloads the response in Chromium, and replaces HTML content
        with an updated version, with JavaScript executed.

        :param retries: The number of times to retry loading the page in Chromium.
        :param script: JavaScript to execute upon page load (optional).
        :param keep_page: If ``True`` will allow you to interact with the browser page through ``r.html.page``.

        :param send_cookies_session: If ``True`` send ``HTMLSession.cookies`` convert.
        :param cookies: If not ``empty`` send ``cookies``.

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

        """

        self.browser = (
            self.session.browser
        )  # Automatically create a event loop and browser
        content = None

        if self.url == DEFAULT_URL:
            render_html = True

        if send_cookies_session:
            cookies = self._convert_cookiesjar_to_render()

        content, result, page = self._render(
            url=self.url,
            script=script,
            content=self.html,
            keep_page=keep_page,
            cookies=cookies,
            render_html=render_html,
        )

        html = HTML(
            url=self.url,
            html=content.encode(DEFAULT_ENCODING),
            default_encoding=DEFAULT_ENCODING,
            session=self.session,
        )
        for k, v in html.__dict__.items():
            setattr(self, k, v)
        self.page = page
        return result

    async def arender(
        self,
        script: Optional[str] = None,
        keep_page: bool = False,
        cookies: Optional[list] = None,
        send_cookies_session: bool = False,
        render_html: bool = False,
    ):
        """Async version of render. Takes same parameters."""

        self.browser = await self.session.browser
        content = None

        if self.url == DEFAULT_URL:
            render_html = True

        if send_cookies_session:
            cookies = self._convert_cookiesjar_to_render()

        content, result, page = await self._async_render(
            url=self.url,
            script=script,
            content=self.html,
            keep_page=keep_page,
            cookies=cookies,
            render_html=render_html,
        )

        html = HTML(
            url=self.url,
            html=content.encode(DEFAULT_ENCODING),
            default_encoding=DEFAULT_ENCODING,
            session=self.session,
        )
        for k, v in html.__dict__.items():
            setattr(self, k, v)
        self.page = page
        return result


class HTMLResponse(requests.Response):
    """An HTML-enabled :class:`requests.Response <requests.Response>` object.
    Effectively the same, but with an intelligent ``.html`` property added.
    """

    def __init__(self, session: _Session) -> None:
        super(HTMLResponse, self).__init__()
        self._html: Optional[HTML] = None
        self.session = session

    @property
    def html(self) -> HTML:
        if self._html is None:
            self._html = HTML(
                session=self.session,
                url=self.url,
                html=self.content,
                default_encoding=self.encoding,
            )

        return self._html

    @classmethod
    def _from_response(cls, session: _Session, response: requests.Response):
        html_r = cls(session=session)
        for k, v in response.__dict__.items():
            setattr(html_r, k, v)
        return html_r


def user_agent(style: Optional[str] = None) -> _UserAgent:
    """Returns an apparently legit user-agent, if not requested one of a specific
    style. Defaults to a Chrome-style User-Agent.
    """
    return UserAgent()[style] if style is not None else DEFAULT_USER_AGENT


def _get_first_or_list(l, first=False):
    return l[0] if first and l else l


def response_hook(
    session: _Session, response: requests.Response, *args, **kwargs
) -> HTMLResponse:
    """Change response encoding and replace it by a HTMLResponse."""
    if not response.encoding:
        response.encoding = DEFAULT_ENCODING
    return HTMLResponse._from_response(session, response)


class HTMLSession(requests.Session):
    def __init__(self, *args, **kwargs):
        super(HTMLSession, self).__init__(*args, **kwargs)
        self.hooks["response"].append(partial(response_hook, self))

    @property
    def browser(self):
        if not hasattr(self, "_browser"):
            self._playwright = sync_playwright().start()
            self._browser = self._playwright.chromium.launch()
        return self._browser

    def close(self):
        """If a browser was created close it first."""
        if hasattr(self, "_browser"):
            self._browser.close()
            self._playwright.stop()
        super().close()


class AsyncHTMLSession(requests.Session):
    """An async consumable session."""

    def __init__(self, loop=None, workers=None, *args, **kwargs):
        """Set or create an event loop and a thread pool.

        :param loop: Asyncio loop to use.
        :param workers: Amount of threads to use for executing async calls.
            If not pass it will default to the number of processors on the
            machine, multiplied by 5."""
        super().__init__(*args, **kwargs)
        self.hooks["response"].append(partial(response_hook, self))

        self.loop = loop or asyncio.get_event_loop()
        self.thread_pool = ThreadPoolExecutor(max_workers=workers)

    def request(self, *args, **kwargs):
        """Partial original request func and run it in a thread."""
        func = partial(super().request, *args, **kwargs)
        return self.loop.run_in_executor(self.thread_pool, func)

    async def close(self):
        """If a browser was created close it first."""
        if hasattr(self, "_browser"):
            await self._browser.close()
            await self._playwright.stop()
        super().close()

    def run(self, *coros):
        """Pass in all the coroutines you want to run, it will wrap each one
        in a task, run it and wait for the result. Return a list with all
        results, this is returned in the same order coros are passed in."""
        tasks = [asyncio.ensure_future(coro()) for coro in coros]
        done, _ = self.loop.run_until_complete(asyncio.wait(tasks))
        return [t.result() for t in done]

    @property
    async def browser(self):
        if not hasattr(self, "_browser"):
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch()
        return self._browser
