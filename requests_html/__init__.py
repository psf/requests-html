import sys

from lxml.html.clean import Cleaner
from fake_useragent import UserAgent

from requests_html.globals import DEFAULT_USER_AGENT
from requests_html.typing import _UserAgent


# Sanity checking.
try:
    assert sys.version_info.major == 3
    assert sys.version_info.minor > 5
except AssertionError:
    raise RuntimeError('Requests-HTML requires Python 3.6+!')


cleaner = Cleaner()
cleaner.javascript = True
cleaner.style = True


class MaxRetries(Exception):

    def __init__(self, message):
        self.message = message


def user_agent(style=None) -> _UserAgent:
    """Returns an apparently legit user-agent, if not requested one of a specific
    style. Defaults to a Chrome-style User-Agent.
    """
    global useragent
    if (not useragent) and style:
        useragent = UserAgent()

    return useragent[style] if style else DEFAULT_USER_AGENT


def _get_first_or_list(l, first=False):
    if first:
        try:
            return l[0]
        except IndexError:
            return None
    else:
        return l
