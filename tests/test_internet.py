import pytest
from requests_html import HTMLSession, AsyncHTMLSession, HTMLResponse

session = HTMLSession()

@pytest.mark.internet
def test_pagination():
    pages = (
        'https://xkcd.com/1957/',
        'https://smile.amazon.com/',
        'https://theverge.com/archives'
    )

    for page in pages:
        r = session.get(page)
        assert next(r.html)

@pytest.mark.internet
@pytest.mark.asyncio
async def test_async_pagination(event_loop):
    asession = AsyncHTMLSession()
    pages = (
        'https://xkcd.com/1957/',
        'https://smile.amazon.com/',
        'https://theverge.com/archives'
    )

    for page in pages:
        r = await asession.get(page)
        assert await r.html.__anext__()

@pytest.mark.internet
def test_async_run():
    asession = AsyncHTMLSession()

    async def test1():
        return await asession.get('https://xkcd.com/1957/')

    async def test2():
        return await asession.get('https://reddit.com/')

    async def test3():
        return await asession.get('https://smile.amazon.com/')

    r = asession.run(test1, test2, test3)

    assert len(r) == 3
    assert isinstance(r[0], HTMLResponse)
