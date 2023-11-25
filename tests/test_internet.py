import pytest

from requests_html_playwright.requests_html import (
    AsyncHTMLSession,
    HTMLResponse,
    HTMLSession,
)

urls = [
    "https://xkcd.com/1957/",
    "https://www.reddit.com/",
    "https://github.com/psf/requests-html/issues",
    "https://discord.com/category/engineering",
    "https://stackoverflow.com/",
    "https://www.frontiersin.org/",
    "https://azure.microsoft.com/en-us",
]


@pytest.mark.parametrize("url", urls)
@pytest.mark.internet
def test_pagination(url: str):
    session = HTMLSession()
    r = session.get(url)
    assert isinstance(r, HTMLResponse)
    assert next(r.html)


@pytest.mark.parametrize("url", urls)
@pytest.mark.internet
@pytest.mark.asyncio
async def test_async_pagination(event_loop, url):
    asession = AsyncHTMLSession()

    r = await asession.get(url)
    assert await r.html.__anext__()


@pytest.mark.internet
def test_async_run():
    asession = AsyncHTMLSession()

    async_list = []
    for url in urls:

        async def _test():
            return await asession.get(url)

        async_list.append(_test)

    r = asession.run(*async_list)

    assert len(r) == len(urls)
    assert isinstance(r[0], HTMLResponse)
