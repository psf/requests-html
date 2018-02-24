import requests
from pyquery import PyQuery

from lxml.etree import tostring
import html2text
html2text = html2text.HTML2Text()

# TODO: Markdown converter.

class Element:
    """docstring for Element"""
    def __init__(self, element):
        self.element = element

    def __repr__(self):
        attrs = []
        for attr in self.attrs:
            attrs.append('{}={}'.format(attr, repr(self.attrs[attr])))

        return "<Element {} {}>".format(repr(self.element.tag), ' '.join(attrs))
        # return tostring(self.element).decode('utf-8')

    @property
    def pq(self):
        return PyQuery(self.element)

    @property
    def attrs(self):
        # print(dir(self.element))
        return {k: self.pq.attr[k] for k in self.element.keys()}

    @property
    def text(self):
        return self.pq.text()

    @property
    def full_text(self):
        return self.pq.text_content()

    @property
    def markdown(self):
        return html2text.handle(self.html)

    @property
    def html(self):
        return tostring(self.element).decode('utf-8').strip()

    def find(self, selector):
        def gen():
            for found in self.pq(selector):
                yield Element(found)

        return [g for g in gen()]



class HTML(object):
    """docstring for HTML"""
    def __init__(self, response):
        self.html = response.text
        self.url = response.url
        self.skip_anchors = True

    def __repr__(self):
        return repr("<HTML url={}>".format(repr(self.url)))

    def find(self, selector=None):
        def gen():
            for found in self.pq(selector):
                yield Element(found)

        return [g for g in gen()]

    @property
    def markdown(self):
        return html2text.handle(self.html)

    @property
    def links(self):
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
        url = '/'.join(self.url.split('/')[:-1])
        if url.endswith('/'):
            url = url[:-1]

        return url

    @property
    def absolute_links(self):
        def gen():
            for link in self.links:
                if not link.startswith('http'):
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
        return PyQuery(self.html)


def handle_response(response, **kwargs):
    response.html = HTML(response)
    return response


session = requests.Session()
session.hooks = {'response': handle_response}

print(session.get('http://httpbin.org/').html.markdown)