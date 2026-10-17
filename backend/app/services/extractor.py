"""Hook for URL -> feature extraction.

There is deliberately NO default extractor. A model trained on content-based
(HTML/DOM) features cannot be fed lexical URL features, so a working extractor
must reproduce exactly the pipeline in your feature_extraction/ code. Until one
is plugged in, POST /api/analyze answers 501 instead of guessing.

To add one later:
    def my_extractor(url: str) -> dict:   # {feature_name: number}, all model columns
        ...
    app = create_app(extractor=my_extractor)

If it fetches pages it MUST be SSRF-hardened (public IPs only, re-validate every
redirect, pin the resolved IP, timeouts, size and content-type limits).
"""
