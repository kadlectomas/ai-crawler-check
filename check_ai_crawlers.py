#!/usr/bin/env python3
"""Check whether AI crawlers may read a web page and whether the server answers them.

Usage:
    python3 check_ai_crawlers.py https://example.com/some/page/

Two checks per crawler:
  1. robots.txt: is the crawler allowed to fetch this URL?
  2. live request: what does the server answer when the request carries the crawler's user agent?
     (A 403 or a challenge page here usually means a CDN or firewall rule, not robots.txt.)

No dependencies, Python 3.8+. The live request is only a hint: real crawlers also come from
known IP ranges, which some firewalls check. Full check with explanations:
https://tomakadlec.com/en/tools/ai-crawler-check/
"""
import sys
import urllib.error
import urllib.request
import urllib.robotparser
from urllib.parse import urlparse

# Crawler name -> user agent string used for the live request.
CRAWLERS = {
    "GPTBot": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)",
    "OAI-SearchBot": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; OAI-SearchBot/1.0; +https://openai.com/searchbot)",
    "ChatGPT-User": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; ChatGPT-User/1.0; +https://openai.com/bot",
    "ClaudeBot": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; ClaudeBot/1.0; +claudebot@anthropic.com)",
    "Claude-User": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Claude-User/1.0; +Claude-User@anthropic.com)",
    "PerplexityBot": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; PerplexityBot/1.0; +https://perplexity.ai/perplexitybot)",
    "Google-Extended": None,  # robots.txt token only, Google fetches with Googlebot
    "Googlebot": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Bingbot": "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
    "CCBot": "CCBot/2.0 (https://commoncrawl.org/faq/)",
}

TIMEOUT = 15


def robots_rules(url):
    parts = urlparse(url)
    robots_url = f"{parts.scheme}://{parts.netloc}/robots.txt"
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
    except Exception as exc:  # network error: treat as unknown
        print(f"robots.txt: could not read {robots_url} ({exc})")
        return None
    return rp


def live_status(url, user_agent):
    req = urllib.request.Request(url, headers={"User-Agent": user_agent})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            body = resp.read(200_000).decode("utf-8", "replace").lower()
            challenge = any(s in body for s in ("cf-challenge", "captcha", "just a moment", "access denied"))
            return resp.status, challenge
    except urllib.error.HTTPError as exc:
        return exc.code, False
    except Exception as exc:
        return f"error: {exc.__class__.__name__}", False


def main():
    if len(sys.argv) != 2 or not sys.argv[1].startswith(("http://", "https://")):
        print(__doc__)
        sys.exit(2)
    url = sys.argv[1]
    rp = robots_rules(url)
    print(f"{'crawler':<16}{'robots.txt':<12}{'live request'}")
    problems = 0
    for name, ua in CRAWLERS.items():
        allowed = "unknown" if rp is None else ("allowed" if rp.can_fetch(name, url) else "BLOCKED")
        if ua is None:
            live = "n/a (robots token only)"
        else:
            status, challenge = live_status(url, ua)
            live = f"{status}" + (" + challenge page" if challenge else "")
            if status != 200 or challenge:
                problems += 1
        if allowed == "BLOCKED":
            problems += 1
        print(f"{name:<16}{allowed:<12}{live}")
    print()
    print("No problems found." if problems == 0 else f"{problems} problem(s) found. See README.md for what each one means.")
    sys.exit(0 if problems == 0 else 1)


if __name__ == "__main__":
    main()
