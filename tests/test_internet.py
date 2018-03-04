from requests_html import HTMLSession

session = HTMLSession()

def test_pagination():
    pages = (
        'https://xkcd.com/1957/',
        'https://reddit.com/',
        'https://pornhub.com/',
        'https://theverge.com/archives'
    )

    for page in pages:
        r = session.get(page)
        assert next(r.html)

