# Web Page to Markdown for LLMs & RAG (Clean Text + Chunks)

[![Run on Apify](https://img.shields.io/badge/Run%20on-Apify-1f6feb?logo=apify)](https://apify.com/manageable_gully/page-to-markdown) [![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **Run it in the cloud with no setup:** [Web Page to Markdown for LLMs & RAG on the Apify Store](https://apify.com/manageable_gully/page-to-markdown).  
> Pay only per result, export to JSON/CSV/Excel, schedule runs and call it from the API.
<!-- Note: the Apify Store page goes live once the Actor is published. -->
<!-- AFFILIATE_LINK_PLACEHOLDER: replace the Apify links above with the affiliate link when available -->

Turn any list of URLs into **clean Markdown** that is ready for ChatGPT, Claude, embeddings or a RAG index. Only the main content is kept. Navigation, footers, cookie banners, scripts and ads are removed, while headings, lists, tables and links are preserved.

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

## Pricing
Pay per event: **$0.001 per page converted** ($1 per 1,000 pages). Pages that fail, return an error or are disallowed by robots.txt are free.

## Limits
- Pages are fetched without running JavaScript, which is fast and cheap. Content that only renders client-side (some single-page apps) may come back thin. Check `wordCount`.
- PDFs and other non-HTML files are rejected with an error and not charged. Use the companion **PDF & Image OCR** Actor for documents.
- Use it only on content you are allowed to process. The Actor doesn't get around paywalls or logins.

*This Actor was built and is maintained with AI assistance. Report issues on the Issues tab; they are monitored daily.*

## Run from source
This repository is the full source of the [Web Page to Markdown for LLMs & RAG](https://apify.com/manageable_gully/page-to-markdown) Actor.

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
