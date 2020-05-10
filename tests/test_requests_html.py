import os
from functools import partial

import pytest
from pyppeteer.browser import Browser
from pyppeteer.page import Page
from requests_html import HTMLSession, AsyncHTMLSession, HTML
from requests_file import FileAdapter

session = HTMLSession()
session.mount('file://', FileAdapter())


def get():
    path = os.path.sep.join((os.path.dirname(os.path.abspath(__file__)), 'python.html'))
    url = 'file://{}'.format(path)

    return session.get(url)


@pytest.fixture
def async_get(event_loop):
    """ AsyncSession cannot be created global since it will create
        a different loop from pytest-asyncio. """
    async_session = AsyncHTMLSession()
    async_session.mount('file://', FileAdapter())
    path = os.path.sep.join((os.path.dirname(os.path.abspath(__file__)), 'python.html'))
    url = 'file://{}'.format(path)

    return partial(async_session.get, url)


def test_file_get():
    r = get()
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_async_file_get(async_get):
    r = await async_get()
    assert r.status_code == 200


def test_class_seperation():
    r = get()

    about = r.html.find('#about', first=True)
    assert len(about.attrs['class']) == 2


def test_css_selector():
    r = get()

    about = r.html.find('#about', first=True)

    for menu_item in (
        'About', 'Applications', 'Quotes', 'Getting Started', 'Help',
        'Python Brochure'
    ):
        assert menu_item in about.text.split('\n')
        assert menu_item in about.full_text.split('\n')


def test_containing():
    r = get()

    python = r.html.find(containing='python')
    assert len(python) == 192

    for e in python:
        assert 'python' in e.full_text.lower()


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


@pytest.mark.asyncio
async def test_async_links(async_get):
    r = await async_get()
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


@pytest.mark.parametrize('url,link,expected', [
    ('http://example.com/', 'test.html', 'http://example.com/test.html'),
    ('http://example.com', 'test.html', 'http://example.com/test.html'),
    ('http://example.com/foo/', 'test.html', 'http://example.com/foo/test.html'),
    ('http://example.com/foo/bar', 'test.html', 'http://example.com/foo/test.html'),
    ('http://example.com/foo/', '/test.html', 'http://example.com/test.html'),
    ('http://example.com/', 'http://xkcd.com/about/', 'http://xkcd.com/about/'),
    ('http://example.com/', '//xkcd.com/about/', 'http://xkcd.com/about/'),
])
def test_absolute_links(url, link, expected):
    head_template = """<head><base href='{}'></head>"""
    body_template = """<body><a href='{}'>Next</a></body>"""

    # Test without `<base>` tag (url is base)
    html = HTML(html=body_template.format(link), url=url)
    assert html.absolute_links.pop() == expected

    # Test with `<base>` tag (url is other)
    html = HTML(
        html=head_template.format(url) + body_template.format(link),
        url='http://example.com/foobar/')
    assert html.absolute_links.pop() == expected


def test_parser():
    doc = """<a href='https://httpbin.org'>httpbin.org\n</a>"""
    html = HTML(html=doc)

    assert html.find('html')
    assert html.element('a').text().strip() == 'httpbin.org'


@pytest.mark.render
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


@pytest.mark.render
@pytest.mark.asyncio
async def test_async_render(async_get):
    r = await async_get()
    script = """
    () => {
        return {
            width: document.documentElement.clientWidth,
            height: document.documentElement.clientHeight,
            deviceScaleFactor: window.devicePixelRatio,
        }
    }
    """
    val = await r.html.arender(script=script)
    for value in ('width', 'height', 'deviceScaleFactor'):
        assert value in val

    about = r.html.find('#about', first=True)
    assert len(about.links) == 6
    await r.html.browser.close()


@pytest.mark.render
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


@pytest.mark.render
@pytest.mark.asyncio
async def test_bare_arender():
    doc = """<a href='https://httpbin.org'>"""
    html = HTML(html=doc, async_=True)
    script = """
        () => {
            return {
                width: document.documentElement.clientWidth,
                height: document.documentElement.clientHeight,
                deviceScaleFactor: window.devicePixelRatio,
            }
        }
    """
    val = await html.arender(script=script, reload=False)
    for value in ('width', 'height', 'deviceScaleFactor'):
        assert value in val

    assert html.find('html')
    assert 'https://httpbin.org' in html.links
    await html.browser.close()


@pytest.mark.render
def test_bare_js_eval():
    doc = """
    <!DOCTYPE html>
    <html>
    <body>
    <div id="replace">This gets replaced</div>

    <script type="text/javascript">
      document.getElementById("replace").innerHTML = "yolo";
    </script>
    </body>
    </html>
    """

    html = HTML(html=doc)
    html.render()

    assert html.find('#replace', first=True).text == 'yolo'


@pytest.mark.render
@pytest.mark.asyncio
async def test_bare_js_async_eval():
    doc = """
    <!DOCTYPE html>
    <html>
    <body>
    <div id="replace">This gets replaced</div>

    <script type="text/javascript">
      document.getElementById("replace").innerHTML = "yolo";
    </script>
    </body>
    </html>
    """

    html = HTML(html=doc, async_=True)
    await html.arender()

    assert html.find('#replace', first=True).text == 'yolo'
    await html.browser.close()


def test_browser_session():
    """ Test browser instaces is created and properly close when session is closed.
        Note: session.close method need to be tested together with browser creation,
            since no doing that will left the browser running. """
    session = HTMLSession()
    assert isinstance(session.browser, Browser)
    assert hasattr(session, "loop") == True
    session.close()
    # assert count_chromium_process() == 0


@pytest.mark.asyncio
async def test_browser_session_fail():
    """ HTMLSession.browser should not be call within an existing event loop> """
    session = HTMLSession()
    with pytest.raises(RuntimeError):
        session.browser


def test_browser_process():
    for _ in range(3):
        r = get()
        r.html.render()

        assert r.html.page == None


@pytest.mark.asyncio
async def test_async_browser_session():
    session = AsyncHTMLSession()
    browser = await session.browser
    assert isinstance(browser, Browser)
    await session.close()


if __name__ == '__main__':
    test_containing()
