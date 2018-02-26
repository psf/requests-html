import os

from requests_html import Session
from requests_file import FileAdapter

session = Session()
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


def test_attrs():
    r = get()
    about = r.html.find('#about', first=True)

    assert 'aria-haspopup' in about.attrs
    assert len(about.attrs['class']) == 2


def test_links():
    r = get()
    about = r.html.find('#about', first=True)

    len(about.links) == 6
    len(about.absolute_links) == 6


def test_search():
    r = get()
    style = r.html.search('Python is a {} language')[0]
    assert style == 'programming'


def test_xpath():
    r = get()
    html = r.html.xpath('/html', first=True)
    assert 'no-js' in html.attrs['class']

if __name__ == '__main__':
    # test_file_get()
    test_css_selector()
