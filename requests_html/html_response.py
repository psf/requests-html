from typing import Union

from requests_html.parsers import HTML

import requests


class HTMLResponse(requests.Response):
    """An HTML-enabled :class:`requests.Response <requests.Response>` object.
    Effectively the same, but with an intelligent ``.html`` property added.
    """

    def __init__(self, session: Union['HTMLSession', 'AsyncHTMLSession']) -> None:
        super(HTMLResponse, self).__init__()
        self._html = None  # type: HTML
        self.session = session

    @property
    def html(self) -> HTML:
        if not self._html:
            self._html = HTML(session=self.session, url=self.url, html=self.content, default_encoding=self.encoding)

        return self._html

    @classmethod
    def _from_response(cls, response, session: Union['HTMLSession', 'AsyncHTMLSession']):
        html_r = cls(session=session)
        html_r.__dict__.update(response.__dict__)
        return html_r

