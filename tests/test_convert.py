import asyncio
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import httpx
import pytest

from src.convert import RobotsCache, chunk_markdown, fetch_html, html_to_markdown, normalize_url
from src.main import parse_input

ARTICLE = """<!doctype html><html lang="en"><head><title>How Widgets Work | Acme Blog</title>
<meta name="description" content="A deep dive into widgets."><meta name="author" content="Dana Levi">
<meta property="article:published_time" content="2026-09-01T10:00:00Z"></head><body>
<nav><a href="/">Home</a> <a href="/blog">Blog</a> <a href="/pricing">Pricing</a></nav>
<article><h1>How Widgets Work</h1>
<p>Widgets are small mechanical devices that turn rotational force into linear motion. This article explains the
three main widget designs, their trade-offs, and how to pick the right one for your factory floor.</p>
<h2>Design one: the classic gear</h2><p>The classic gear widget uses a pair of meshed gears. It is cheap, robust and
easy to repair, which is why it remains the most common design in small workshops. See <a href="https://example.org/gears">gear basics</a>.</p>
<h2>Comparison</h2><table><tr><th>Design</th><th>Cost</th></tr><tr><td>Gear</td><td>Low</td></tr><tr><td>Belt</td><td>Medium</td></tr></table>
<p>In summary, choose the gear design unless you need silent operation, in which case a belt drive is better.</p>
</article><footer>Copyright Acme 2026. All rights reserved. Cookie settings.</footer>
<script>var tracking = "should not appear";</script></body></html>"""


def test_normalize():
    assert normalize_url('example.com/a#x') == 'https://example.com/a'
    with pytest.raises(ValueError):
        normalize_url('ftp://x.y')
    with pytest.raises(ValueError):
        normalize_url('bad host!')


def test_article_extraction():
    r = html_to_markdown(ARTICLE, 'https://acme.test/blog/widgets')
    md = r['markdown']
    assert r['extractionMode'] == 'article' and r['title'].startswith('How Widgets Work')
    assert '## Design one' in md or 'Design one: the classic gear' in md
    assert 'Pricing' not in md and 'should not appear' not in md and 'Cookie settings' not in md
    assert '[gear basics](https://example.org/gears)' in md
    assert '| Gear' in md and r['author'] == 'Dana Levi' and r['publishedDate'].startswith('2026-09-01')
    assert r['language'] == 'en' and r['wordCount'] > 50


def test_full_mode_and_link_stripping():
    r = html_to_markdown(ARTICLE, 'https://acme.test/', mode='full', include_links=False)
    assert r['extractionMode'] == 'full' and 'should not appear' not in r['markdown']
    assert 'Pricing' not in r['markdown']  # nav removed
    assert '](https://example.org/gears)' not in r['markdown'] and 'gear basics' in r['markdown']


def test_landing_page_falls_back_to_full():
    html = '<html><head><title>Landing</title></head><body><div><h2>Fast</h2><p>Short.</p></div></body></html>'
    r = html_to_markdown(html, 'https://a.test/')
    assert r['extractionMode'] == 'full' and '## Fast' in r['markdown'] and r['markdown'].startswith('# Landing')


def test_hebrew_rtl_page():
    html = '<html lang="he" dir="rtl"><head><title>מדריך</title></head><body><article><h1>מדריך קצר</h1>' + \
           '<p>' + 'זהו מאמר בעברית שמסביר איך להשתמש בכלי בצורה נכונה ויעילה. ' * 8 + '</p></article></body></html>'
    r = html_to_markdown(html, 'https://a.test/he')
    assert 'זהו מאמר בעברית' in r['markdown'] and r['language'] == 'he'


def test_chunking():
    md = '# T\n\n' + '\n\n'.join(f'## S{i}\n\n' + ('word ' * 120) for i in range(10))
    chunks = chunk_markdown(md, 1000, 100)
    assert len(chunks) > 3 and all(len(c) <= 1000 + 102 for c in chunks)
    assert chunk_markdown('short', 1000) == ['short'] and chunk_markdown('', 10) == []
    long = 'x' * 5000
    assert all(len(c) <= 1000 for c in chunk_markdown(long, 1000, 100))


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        routes = {'/robots.txt': (200, 'text/plain', 'User-agent: *\nDisallow: /private\n'),
                  '/a': (200, 'text/html; charset=utf-8', ARTICLE), '/private/x': (200, 'text/html', ARTICLE),
                  '/file.pdf': (200, 'application/pdf', '%PDF-1.4')}
        if self.path == '/old':
            self.send_response(301); self.send_header('Location', '/a'); self.end_headers(); return
        code, ctype, body = routes.get(self.path, (404, 'text/plain', 'nf'))
        self.send_response(code); self.send_header('Content-Type', ctype); self.end_headers(); self.wfile.write(body.encode())


@pytest.fixture(scope='module')
def server():
    srv = ThreadingHTTPServer(('127.0.0.1', 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f'http://127.0.0.1:{srv.server_address[1]}'
    srv.shutdown()


def test_fetch_robots_redirect(server):
    async def go():
        async with httpx.AsyncClient(timeout=5) as c:
            rc = RobotsCache(c)
            assert await rc.allowed(server + '/a') and not await rc.allowed(server + '/private/x')
            html, final, status, ctype = await fetch_html(c, server + '/old', allow_private=True)
            assert final.endswith('/a') and status == 200 and 'Widgets' in html
            with pytest.raises(Exception, match='non-public'):
                await fetch_html(c, server + '/a')
    asyncio.run(go())


def test_parse_input():
    urls, inv, cfg = parse_input({'startUrls': [{'url': 'a.com'}, {'url': 'https://a.com/'}, {'url': 'bad host!'}], 'chunkSize': 99999})
    assert urls == ['https://a.com/'] and len(inv) == 1 and cfg['chunk'] == 20000
    with pytest.raises(ValueError):
        parse_input({'startUrls': []})
