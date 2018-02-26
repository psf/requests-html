import requests
from pyquery import PyQuery

from fake_useragent import UserAgent
from lxml import etree
from lxml.html.soupparser import fromstring
from parse import search as parse_search
from parse import findall


useragent = UserAgent()


class BaseParser:
    """docstring for BaseParser"""
    def __init__(self, *, element, html=None, url):
        self.element = element
        self.url = url
        self.skip_anchors = True

        if not html:
            self.html = etree.tostring(self.element).decode('utf-8').strip()
        else:
            self.html = html

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
        return self.pq.text_content()

    def find(self, selector, first=False):
        """Given a jQuery selector, returns a list of element objects."""
        def gen():
            for found in self.pq(selector):
                yield Element(element=found, url=self.url)

        c = [g for g in gen()]

        if first:
            try:
                return c[0]
            except IndexError:
                return None
        else:
            return c

    def xpath(self, selector, first=False):
        """Given an XPath selector, returns a list of element objects."""
        c = [Element(element=e, url=self.url) for e in self.lxml.xpath(selector)]
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
                # Appears to not be an absolute link.
                if ':' not in link:
                    if link.startswith('/'):
                        href = '{}{}'.format(self.base_url, link)
                    else:
                        href = '{}/{}'.format(self.base_url, link)
                else:
                    href = link

                yield href

        return set(g for g in gen())

    @property
    def base_url(self):
        """The base URL for the page."""
        url = '/'.join(self.url.split('/')[:-1])
        if url.endswith('/'):
            url = url[:-1]

        return url


class Element(BaseParser):
    """An element of HTML."""
    def __init__(self, *, element, url):
        super(Element, self).__init__(element=element, url=url)
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
    def __init__(self, *, response):
        super(HTML, self).__init__(
            element=fromstring(response.text),
            html=response.text,
            url=response.url
        )

    def __repr__(self):
        return "<HTML url={}>".format(repr(self.url))


def _handle_response(response, **kwargs):
    """Requests HTTP Response handler. Attaches .html property to Response
    objects.
    """

    response.html = HTML(response=response)
    return response


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
    amongst other things."""
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

        response.html = HTML(response=response)
        return response

# Backwards compatiblity.
session = Session()
