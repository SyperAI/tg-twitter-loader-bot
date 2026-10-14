import re

# Matches Twitter and X tweet/status URLs
TWITTER_STATUS_PATTERN = re.compile(
    r"https?://(?:(?:www|mobile|m)\.)?(?:twitter\.com|x\.com)/(?P<user>[A-Za-z0-9_]+)/status/(?P<id>\d+)",
    re.IGNORECASE,
)


def extract_twitter_urls(text: str) -> list[str]:
    """
    Extracts and normalizes Twitter / X status URLs from text.
    Removes tracking parameters and duplicates while preserving order.
    """
    found_urls: list[str] = []
    seen_ids: set[str] = set()

    for match in TWITTER_STATUS_PATTERN.finditer(text):
        tweet_id = match.group("id")
        user = match.group("user")
        if tweet_id not in seen_ids:
            seen_ids.add(tweet_id)
            # Canonical URL format
            canonical_url = f"https://x.com/{user}/status/{tweet_id}"
            found_urls.append(canonical_url)

    return found_urls
