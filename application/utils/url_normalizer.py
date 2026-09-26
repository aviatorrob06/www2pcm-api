from urllib.parse import urlsplit, urlunsplit, quote


def normalize(url: str) -> str:
    parts = urlsplit(url)

    if parts.scheme not in ("http", "https"):
        raise ValueError("URL must use HTTP or HTTPS")

    if not parts.netloc:
        raise ValueError("URL must contain a host")

    path = quote(parts.path, safe="/%:@!$&'()*+,;=-._~")

    query = quote(parts.query, safe="=&%:@!$'()*+,;/?-._~")

    fragment = quote(parts.fragment, safe="=%:@!$&'()*+,;/?-._~")

    return urlunsplit((
        parts.scheme,
        parts.netloc,
        path,
        query,
        fragment
    ))