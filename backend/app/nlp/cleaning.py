import html
import re

TAG_PATTERN = re.compile(r"<[^>]+>")  # matches anything between < and >, like <br /> or <b>
WHITESPACE_PATTERN = re.compile(r"\s+")  # matches any run of spaces, tabs, or newlines


def clean_text(text: str) -> str:
    text = html.unescape(text)  # turns &amp; into &, &#39; into ', etc
    text = TAG_PATTERN.sub(" ", text)  # replace tags with a space so words dont get glued together
    text = WHITESPACE_PATTERN.sub(" ", text).strip()  # collapse the spaces left behind, trim the ends
    return text
