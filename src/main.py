"""Apify entrypoint: web pages -> clean Markdown for LLMs/RAG (robots.txt respected)."""
from __future__ import annotations

import asyncio
import datetime as dt
import os

import httpx
from apify import Actor

from .convert import USER_AGENT, RobotsCache, chunk_markdown, fetch_html, html_to_markdown, normalize_url

EVENT = 'page-converted'


def parse_input(inp: dict) -> tuple[list[str], list[dict], dict]:
    raw = [s.get('url') if isinstance(s, dict) else s for s in (inp.get('startUrls') or inp.get('urls') or [])]
    urls, invalid = [], []
    for u in raw:
        if not u or not str(u).strip():
            continue
        try:
            n = normalize_url(str(u))
            if n not in urls:
                urls.append(n)
        except ValueError as e:
            invalid.append({'url': u, 'error': str(e)})
    if not urls and not invalid:
        raise ValueError('Provide at least one URL in "startUrls".')
    mode = inp.get('extractionMode', 'article')
    if mode not in ('article', 'full'):
        raise ValueError('extractionMode must be article or full')
    cfg = {'mode': mode, 'links': bool(inp.get('includeLinks', True)), 'images': bool(inp.get('includeImages', False)),
           'tables': bool(inp.get('includeTables', True)), 'chunk': int(min(max(inp.get('chunkSize', 0), 0), 20000)),
           'overlap': int(min(max(inp.get('chunkOverlap', 200), 0), 2000)),
           'concurrency': int(min(max(inp.get('maxConcurrency', 10), 1), 50)),
           'timeout': float(min(max(inp.get('timeoutSecs', 30), 5), 120)), 'html': bool(inp.get('includeRawHtml', False))}
    return urls, invalid, cfg


async def main() -> None:
    async with Actor:
        inp = await Actor.get_input() or {}
        try:
            urls, invalid, cfg = parse_input(inp)
        except ValueError as e:
            await Actor.fail(status_message=str(e))
            return
        allow_private = os.environ.get('ALLOW_PRIVATE_NETWORK_FOR_LOCAL_DEV') == '1' and not Actor.is_at_home()
        for bad in invalid:
            await Actor.push_data(bad)
        sem, stop, done = asyncio.Semaphore(cfg['concurrency']), asyncio.Event(), 0
        async with httpx.AsyncClient(timeout=cfg['timeout'], headers={'User-Agent': USER_AGENT}) as client:
            robots = RobotsCache(client)

            async def work(url: str) -> None:
                nonlocal done
                async with sem:
                    if stop.is_set():
                        return
                    item: dict = {'url': url, 'crawledAt': dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')}
                    try:
                        if not await robots.allowed(url):
                            raise PermissionError('disallowed by robots.txt')
                        html, final, status, ctype = await fetch_html(client, url, allow_private=allow_private)
                        if status >= 400:
                            raise ValueError(f'HTTP {status}')
                        if 'html' not in ctype and not html.lstrip().startswith('<'):
                            raise ValueError(f'not an HTML page ({ctype or "unknown type"})')
                        res = await asyncio.to_thread(html_to_markdown, html, final, cfg['mode'], cfg['links'],
                                                      cfg['images'], cfg['tables'])
                        item.update({'finalUrl': final, 'statusCode': status, **res})
                        if cfg['chunk']:
                            item['chunks'] = chunk_markdown(res['markdown'], cfg['chunk'], cfg['overlap'])
                        if cfg['html']:
                            item['html'] = html
                    except Exception as e:  # noqa: BLE001
                        item['error'] = f'{type(e).__name__}: {e}'[:300]
                    if stop.is_set():
                        return
                    if 'error' in item:
                        await Actor.push_data(item)
                    else:
                        r = await Actor.push_data(item, charged_event_name=EVENT)
                        if r.event_charge_limit_reached:
                            stop.set()
                        if r.charged_count == 0 and r.event_charge_limit_reached:
                            return  # not delivered, not charged
                    done += 1
                    if done % 25 == 0:
                        await Actor.set_status_message(f'Converted {done}/{len(urls)}')

            await asyncio.gather(*(work(u) for u in urls))
        await Actor.set_status_message(f'Done: {done}/{len(urls)} pages' + (' (stopped: max charge reached)' if stop.is_set() else ''),
                                       is_terminal=True)
