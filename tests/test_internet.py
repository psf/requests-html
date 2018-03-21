import pytest
from requests_html import HTMLSession, AsyncHTMLSession

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


@pytest.mark.asyncio
async def test_pagination(event_loop):
    asession = AsyncHTMLSession()
    pages = (
        'https://xkcd.com/1957/',
        'https://reddit.com/',
        'https://smile.amazon.com/',
        'https://theverge.com/archives'
    )

    for page in pages:
        r = await asession.get(page)
        assert await r.html.__anext__()
