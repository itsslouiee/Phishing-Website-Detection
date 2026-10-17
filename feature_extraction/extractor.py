"""Turn a URL (and its HTML) into the 70 features used by the model."""
from . import feature_Generator_with_brands as g

URL_MEAN_CUTOFF = 50      # recovered from data.csv
DOMAIN_MEAN_CUTOFF = 27   # recovered from data.csv

# the dataset spells this column differently from the authors' code
RENAMES = {"presence_of_url_shortener": "presence_of_url_shortner"}
NOT_FEATURES = ("serial_number", "url", "label")


def url_to_features(url, html=""):
    raw = g.extract_features(0, url, 0, html, URL_MEAN_CUTOFF, DOMAIN_MEAN_CUTOFF)
    return {RENAMES.get(k, k): v for k, v in raw.items() if k not in NOT_FEATURES}
