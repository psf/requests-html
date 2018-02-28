import os

from requests_html import HTMLSession, HTML
from requests_file import FileAdapter

session = HTMLSession()
session.mount('file://', FileAdapter())


def get():
    path = os.path.sep.join((os.path.dirname(os.path.abspath(__file__)), 'python.html'))
    url = 'file://{}'.format(path)

    return session.get(url)


def test_file_get():
    r = get()
    assert r.status_code == 200


def test_css_selector():
    r = get()

    about = r.html.find('#about', first=True)

    for menu_item in (
        'About', 'Applications', 'Quotes', 'Getting Started', 'Help',
        'Python Brochure'
    ):
        assert menu_item in about.text.split('\n')
        assert menu_item in about.full_text.split('\n')


def test_attrs():
    r = get()
    about = r.html.find('#about', first=True)

    assert 'aria-haspopup' in about.attrs
    assert len(about.attrs['class']) == 2


def test_links():
    r = get()
    about = r.html.find('#about', first=True)

    assert len(about.links) == 6
    assert len(about.absolute_links) == 6


def test_search():
    r = get()
    style = r.html.search('Python is a {} language')[0]
    assert style == 'programming'


def test_xpath():
    r = get()
    html = r.html.xpath('/html', first=True)
    assert 'no-js' in html.attrs['class']

    a_hrefs = r.html.xpath('//a/@href')
    assert '#site-map' in a_hrefs


def test_html_loading():
    doc = """<a href='https://httpbin.org'>"""
    html = HTML(html=doc)

    assert 'https://httpbin.org' in html.links
    assert isinstance(html.raw_html, bytes)
    assert isinstance(html.html, str)


def test_anchor_links():
    r = get()
    r.html.skip_anchors = False

    assert '#site-map' in r.html.links


def test_render():
    r = get()
    script = """
    () => {
        return {
            width: document.documentElement.clientWidth,
            height: document.documentElement.clientHeight,
            deviceScaleFactor: window.devicePixelRatio,
        }
    }
    """
    val = r.html.render(script=script)
    for value in ('width', 'height', 'deviceScaleFactor'):
        assert value in val

    about = r.html.find('#about', first=True)
    assert len(about.links) == 6


def test_bare_render():
    doc = """<a href='https://httpbin.org'>"""
    html = HTML(html=doc)
    script = """
        () => {
            return {
                width: document.documentElement.clientWidth,
                height: document.documentElement.clientHeight,
                deviceScaleFactor: window.devicePixelRatio,
            }
        }
    """
    val = html.render(script=script, reload=False)
    for value in ('width', 'height', 'deviceScaleFactor'):
        assert value in val

    assert html.find('html')
    assert 'https://httpbin.org' in html.links


if __name__ == '__main__':
    test_xpath()
