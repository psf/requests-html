import requests
from pyquery import PyQuery

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


class HTML(object):
    """docstring for HTML"""
    def __init__(self, response):
        self.html = response.text
        self.url = response.url
        self.skip_anchors = True

    def __repr__(self):
        return repr(self.html)

    def find(self, selector):
        def gen():
            for found in self.pq(selector):
                yield Element(found)

        return [g for g in gen()]

    @property
    def links(self):
        def gen():
            for link in self.find('a'):
                href = link.attrs['href']
                if not href.startswith('#') and self.skip_anchors:
                    yield href
        return [g for g in gen()]

    @property
    def base_url(self):
        return '/'.join(self.url.split('/')[:-1])

    @property
    def absolute_links(self):
        def gen():
            for link in self.links:
                if not link.startswith('http'):
                    href = '{}/{}'.format(self.base_url, link)

                yield href

        return [g for g in gen()]

    @property
    def pq(self):
        return PyQuery(self.html)



def handle_response(response, **kwargs):
    response.html = HTML(response)
    return response

session = requests.Session()
session.hooks = {'response': handle_response}

r = session.get('https://pythonhosted.org/pyquery/')
print(r.html.absolute_links)
