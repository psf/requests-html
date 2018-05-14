import os
from urllib import parse

from requests_html import HTMLSession, HTML

session = HTMLSession()

def test_pagination():
    pages = (
        'https://xkcd.com/1957/',
        'https://reddit.com/',
        'https://smile.amazon.com/',
        'https://theverge.com/archives'
    )

    for page in pages:
        r = session.get(page)
        assert next(r.html)


def test_real_pagination():
    class HN_HTML(HTML):
        def _next(self, fetch: bool = False):
            url = list(self.find('.morelink', first=True).absolute_links)[0]
            if fetch:
                return self.session.get(url)
            else:
                return url

    url = 'https://news.ycombinator.com/'
    sample_path = path = os.path.sep.join((os.path.dirname(os.path.abspath(__file__)), 'hn-sample.html'))
    html = open(sample_path).read()
    page = HN_HTML(html=html, url=url)
    next_url = page._next()
    assert parse.urlparse(url).netloc == parse.urlparse(next_url).netloc
