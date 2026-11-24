# ai-crawler-check

Can ChatGPT, Claude, Perplexity and Google's AI read your website? A small script that checks it in one command.

```bash
python3 check_ai_crawlers.py https://example.com/pricing/
```

```
crawler         robots.txt  live request
GPTBot          allowed     200
OAI-SearchBot   allowed     200
ChatGPT-User    allowed     403
ClaudeBot       BLOCKED     200
...
2 problem(s) found. See README.md for what each one means.
```

No dependencies. Python 3.8 or newer.

## What it checks

For each AI crawler it runs two checks:

1. **robots.txt**: may this crawler fetch this URL? A `Disallow` for `GPTBot`, `ClaudeBot` or `*` keeps the page out of that engine.
2. **Live request**: what does your server answer when the request carries the crawler's user agent? A `403`, a `503` or a challenge page here usually comes from a CDN or firewall rule (bot protection), not from robots.txt. Many sites block AI crawlers this way without knowing it.

## The crawlers

| Crawler | Company | What it is for |
|---|---|---|
| GPTBot | OpenAI | collects pages for model training |
| OAI-SearchBot | OpenAI | builds the index for ChatGPT search answers |
| ChatGPT-User | OpenAI | fetches a page when a user asks ChatGPT about it |
| ClaudeBot | Anthropic | collects pages for model training |
| Claude-User | Anthropic | fetches a page when a user asks Claude about it |
| PerplexityBot | Perplexity | builds the index for Perplexity answers |
| Google-Extended | Google | robots.txt token only: use of your pages for Gemini training |
| Googlebot | Google | Search and AI Overviews |
| Bingbot | Microsoft | Bing, also used by Copilot and other assistants |
| CCBot | Common Crawl | open web archive many models are trained on |

Blocking training crawlers (GPTBot, ClaudeBot, Google-Extended, CCBot) is a business choice. Blocking the search and user crawlers (OAI-SearchBot, ChatGPT-User, Claude-User, PerplexityBot, Googlebot, Bingbot) means the assistants can not read your page when someone asks about you.

## robots.txt you can copy

Allow the assistants to read and cite you, keep training out:

```
# AI search and user-triggered fetches: allowed
User-agent: OAI-SearchBot
User-agent: ChatGPT-User
User-agent: Claude-User
User-agent: PerplexityBot
Allow: /

# Model training: blocked
User-agent: GPTBot
User-agent: ClaudeBot
User-agent: Google-Extended
User-agent: CCBot
Disallow: /

User-agent: *
Allow: /
```

Allow everything (the most visibility):

```
User-agent: *
Allow: /
```

## Limits

- The live request uses the crawler's user agent from your machine. Real crawlers also come from published IP ranges, and some firewalls check those. A `200` here is a good sign, not a guarantee.
- Pages that render their text only with JavaScript look empty to most AI crawlers, even when they are allowed. View the page source (not the browser view) to see what a crawler gets.
- User agent strings change. Check the vendors' own docs if a result looks odd.

## Full check

The free web version also checks JavaScript-only content, meta robots tags and `X-Robots-Tag` headers, and explains each result: [AI crawler check](https://tomakadlec.com/en/tools/ai-crawler-check/?utm_source=github&utm_medium=referral&utm_campaign=ai-crawler-check).

Made by [Tomas Kadlec](https://tomakadlec.com/en/?utm_source=github&utm_medium=referral&utm_campaign=ai-crawler-check). I put AI agents to work. I show the numbers.

## License

MIT
