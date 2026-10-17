# Web Page to Markdown & Article Extractor: Clean Text and RAG Chunks for LLMs

[![Run on Apify](https://img.shields.io/badge/Run%20on-Apify-1f6feb?logo=apify)](https://apify.com/manageable_gully/page-to-markdown) [![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **Run it in the cloud with no setup:** [Web Page to Markdown & Article Extractor for LLMs and RAG on the Apify Store](https://apify.com/manageable_gully/page-to-markdown).  
> Pay only per result, export to JSON/CSV/Excel, schedule runs and call it from the API.
<!-- AFFILIATE_LINK_PLACEHOLDER: replace the Apify links above with the affiliate link when available -->

Turn any list of URLs into **clean Markdown** that is ready for ChatGPT, Claude, embeddings or a RAG index. Only the main content is kept. Navigation, footers, cookie banners, scripts and ads are removed, while headings, lists, tables and links are preserved.

## What you can use it for
- **RAG and vector databases:** turn documentation, help-center and blog URLs into clean Markdown chunks for embeddings.
- **AI agents:** give ChatGPT, Claude or your own agent the readable text of a page instead of raw HTML (fewer tokens, better answers).
- **Article extraction:** collect title, author, date and body text from news and blog articles.
- **Content migration:** convert old HTML pages to Markdown for a static site or a new CMS.
- **Summaries and monitoring:** feed the text to an LLM for summaries; pair it with the [RSS Feed Reader](https://apify.com/manageable_gully/rss-feed-reader) for new articles.

## How to use it
1. Add URLs under **Start URLs**.
2. Choose `article` mode (main content) or `full` mode (whole page body).
3. Optionally set **chunk size** and **overlap** for RAG.
4. Click **Start** and use the `markdown` or `chunks` fields.

## Features
- **Main-content extraction** (Trafilatura). It falls back automatically to the full page body on landing pages that have no clear article.
- **Metadata:** title, description, author, published date, site name, language, word count, estimated tokens.
- **RAG chunks:** optional heading- and paragraph-aware splitting with overlap.
- **Any language,** including right-to-left Hebrew and Arabic pages.
- **Polite:** respects robots.txt, fetches each URL once (no crawling), never logs in, and refuses private or internal addresses.

## Input
```json
{ "startUrls": [{"url": "https://en.wikipedia.org/wiki/Markdown"}], "extractionMode": "article", "chunkSize": 1500, "chunkOverlap": 200 }
```

## Output (one item per URL)
```json
{
  "url": "https://en.wikipedia.org/wiki/Markdown", "statusCode": 200, "title": "Markdown",
  "author": null, "publishedDate": "2026-10-01", "language": "en", "extractionMode": "article",
  "wordCount": 6134, "estimatedTokens": 11000,
  "markdown": "# Markdown\n\n**Markdown** is a lightweight markup language ...",
  "chunks": ["# Markdown\n\n...", "## History\n\n..."]
}
```

## Limits
- Pages are fetched without running JavaScript, which is fast and cheap. Content that only renders client-side (some single-page apps) may come back thin. Check `wordCount`.
- PDFs and other non-HTML files are rejected with an error and not charged. Use the [PDF & Image OCR Extractor](https://apify.com/manageable_gully/pdf-ocr-extractor) Actor for documents.
- Use it only on content you are allowed to process. The Actor doesn't get around paywalls or logins.

## Pricing
Pay per event, no monthly rent: **$0.001 per page converted** (**$1.00 per 1,000**).

| Example | Cost |
|---|---|
| 1,000 pages | $1.00 |
| 10,000 pages | $10.00 |
| 100,000 pages | $100.00 |

Pages that fail, return an error or are disallowed by robots.txt are free.

You can set a **maximum cost per run** in the run options; the Actor stops cleanly when it is reached. New to Apify? The free plan includes $5 of platform credit every month, so you can try this Actor at no cost.

## API, integrations and AI agents (MCP)
Run it from your own code with the [Apify API](https://docs.apify.com/api/v2) and get the results in one call:
```bash
curl -X POST "https://api.apify.com/v2/acts/manageable_gully~page-to-markdown/run-sync-get-dataset-items?token=<YOUR_APIFY_TOKEN>" \
  -H "Content-Type: application/json" -d @input.json
```
```python
from apify_client import ApifyClient
run = ApifyClient("<YOUR_APIFY_TOKEN>").actor("manageable_gully/page-to-markdown").call(run_input={...})
```
- **No-code:** use the Apify app in **n8n, Make or Zapier** ("Run Actor", then "Get dataset items"), or send results to Google Sheets, Slack or a webhook.
- **AI agents (MCP):** add `https://mcp.apify.com?tools=manageable_gully/page-to-markdown` to Claude, Cursor, VS Code or any MCP client and the agent can call this Actor as a tool.
- **Schedules:** run it hourly, daily or weekly from Apify Console.

## FAQ
**Does it crawl a whole website?** No. It converts exactly the URLs you give it, which keeps cost predictable. Get the URL list from a sitemap first.

**How is it different from Website Content Crawler?** It is a lightweight, no-browser converter for known URLs: cheaper and faster, but it doesn't crawl or render JavaScript.

**Can AI agents use it?** Yes. It is available as a tool through the Apify MCP server (`https://mcp.apify.com?tools=manageable_gully/page-to-markdown`) and the Apify API, and it returns structured JSON that agents can read directly.

## More tools from WebIntel Tools
- [PDF & Image OCR Extractor](https://apify.com/manageable_gully/pdf-ocr-extractor): PDFs and images to text, Markdown and tables (incl. Hebrew/Arabic)
- [RSS Feed Reader & Monitor](https://apify.com/manageable_gully/rss-feed-reader): read and monitor RSS, Atom and JSON feeds, only new items
- [Website Screenshot & URL to PDF](https://apify.com/manageable_gully/url-to-pdf-screenshot): full-page screenshots and PDFs of URLs or your own HTML
- [Broken Link Checker](https://apify.com/manageable_gully/broken-link-checker): crawl a site and find every 404, broken image and bad redirect

See [all WebIntel Tools Actors](https://apify.com/manageable_gully).

*Made by WebIntel Tools. This Actor was built and is maintained with AI assistance. Report issues on the Issues tab; they are monitored daily.*

## Run from source
This repository is the full source of the [Web Page to Markdown & Article Extractor for LLMs and RAG](https://apify.com/manageable_gully/page-to-markdown) Actor.

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
pytest
# run locally with the Apify CLI (https://docs.apify.com/cli):
apify run --input '{...}'
```

Deploy your own copy with `apify push`. The easiest way to use it is the hosted version on the [Apify Store](https://apify.com/manageable_gully/page-to-markdown).

<!-- AFFILIATE_LINK_PLACEHOLDER: "New to Apify? Sign up here" link goes here -->

## License
MIT, see [LICENSE](LICENSE).
