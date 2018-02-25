import html2text
import requests
from pyquery import PyQuery

from fake_useragent import UserAgent
from lxml import etree
from lxml.html.soupparser import fromstring
from parse import search as parse_search
from parse import findall

# HTML 2 Markdown converter.
html2text = html2text.HTML2Text()
useragent = UserAgent()

# xpath support next.
# parse support.

class Element:
    """An element of HTML."""
    def __init__(self, element):
        self.element = element

    def __repr__(self):
        attrs = []
        for attr in self.attrs:
            attrs.append('{}={}'.format(attr, repr(self.attrs[attr])))

        return "<Element {} {}>".format(repr(self.element.tag), ' '.join(attrs))

    @property
    def pq(self):
        """PyQuery representation of the element."""
        return PyQuery(self.element)

    @property
    def lxml(self):
        return fromstring(self.html)

    @property
    def attrs(self):
        """Returns a dictionary of the attributes of the element."""
        return {k: self.pq.attr[k] for k in self.element.keys()}

    @property
    def text(self):
        """The text content of the element."""
        return self.pq.text()

    @property
    def full_text(self):
        """The full text content (including links) of the element."""
        return self.pq.text_content()

    @property
    def markdown(self):
        """Markdown representation of the element."""
        return html2text.handle(self.html)

    @property
    def html(self):
        """HTML representation of the element."""
        return etree.tostring(self.element).decode('utf-8').strip()

    def find(self, selector, first=False):
        """Given a jQuery selector, returns a list of element objects."""
        def gen():
            for found in self.pq(selector):
                yield Element(found)

        c = [g for g in gen()]

        if first:
            try:
                return c[0]
            except IndexError:
                return None
        else:
            return c

    def xpath(self, selector):
        """Given an XPath selector, returns a list of element objects."""
        return [Element(e) for e in self.lxml.xpath(selector)]

    def search(self, template):
        """Searches the element for the given parse template."""
        return parse_search(template, self.html)

    def search_all(self, template):
        """Searches the element (multiple times) for the given parse
        template.
        """
        return [r for r in findall(template, self.html)]


class HTML:
    """An HTML document."""
    def __init__(self, response):
        self.html = response.text
        self.url = response.url
        self.skip_anchors = True

    def __repr__(self):
        return "<HTML url={}>".format(repr(self.url))

    def find(self, selector, first=False):
        """Given a jQuery selector, returns a list of element objects."""
        def gen():
            for found in self.pq(selector):
                yield Element(found)

        c = [g for g in gen()]

        if first:
            try:
                return c[0]
            except IndexError:
                return None
        else:
            return c

    def search(self, template):
        """Searches the page for the given parse template."""
        return parse_search(template, self.html)

    def search_all(self, template):
        """Searches the page (multiple times) for the given parse template."""
        return [r for r in findall(template, self.html)]

    @property
    def markdown(self):
        """Markdown representation of the page."""
        return html2text.handle(self.html)

    @property
    def links(self):
        """All found links on page, in as–is form."""
        def gen():
            for link in self.find('a'):
                try:
                    href = link.attrs['href']
                    if not href.startswith('#') and self.skip_anchors:
                        yield href
                except KeyError:
                    pass

        return set(g for g in gen())

    @property
    def base_url(self):
        """The base URL for the page."""
        url = '/'.join(self.url.split('/')[:-1])
        if url.endswith('/'):
            url = url[:-1]

        return url

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
    def pq(self):
        """PyQuery representation of the page."""
        return PyQuery(self.html)

    @property
    def lxml(self):
        """Etree representation of the page."""
        return fromstring(self.html)

    def xpath(self, selector):
        """Given an XPath selector, returns a list of element objects."""
        return [Element(e) for e in self.lxml.xpath(selector)]


def _handle_response(response, **kwargs):
    """Requests HTTP Response handler. Attaches .html property to Response
    objects.
    """

    response.html = HTML(response)
    return response


def user_agent(style=None):
    """Returns a random user-agent, if not requested one of a specific
    style.
    """

    if not style:
        return useragent.random
    else:
        return useragent[style]

def get_session(mock_browser=True):
    """Returns a consumable session, for cookie persistience and connection
    pooling, amongst other things.
    """

    # Requests Session.
    session = requests.Session()

    # Mock a web browser's user agent.
    if mock_browser:
        session.headers['User-Agent'] = user_agent()

    # Hook into Requests.
    session.hooks = {'response': _handle_response}

    return session

session = get_session()
