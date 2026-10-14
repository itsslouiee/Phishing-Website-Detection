import re
from urllib.parse import urlparse


# BINARY FEATURES (return 0 or 1)
def has_title(soup):
    if soup.title is None:
        return 0
    return 1 if len(soup.title.text) > 0 else 0


def has_input(soup):
    return 1 if len(soup.find_all("input")) > 0 else 0


def has_button(soup):
    return 1 if len(soup.find_all("button")) > 0 else 0


def has_image(soup):
    return 1 if len(soup.find_all("image")) > 0 else 0


def has_submit(soup):
    for tag in soup.find_all("input"):
        if tag.get("type") == "submit":
            return 1
    return 0


def has_link(soup):
    return 1 if len(soup.find_all("link")) > 0 else 0


def has_password(soup):
    for tag in soup.find_all("input"):
        if (tag.get("type") or tag.get("name") or tag.get("id")) == "password":
            return 1
    return 0


def has_email_input(soup):
    for tag in soup.find_all("input"):
        if (tag.get("type") or tag.get("id") or tag.get("name")) == "email":
            return 1
    return 0


def has_hidden_element(soup):
    for tag in soup.find_all("input"):
        if tag.get("type") == "hidden":
            return 1
    return 0


def has_audio(soup):
    return 1 if len(soup.find_all("audio")) > 0 else 0


def has_video(soup):
    return 1 if len(soup.find_all("video")) > 0 else 0


def has_h1(soup):
    return 1 if len(soup.find_all("h1")) > 0 else 0


def has_h2(soup):
    return 1 if len(soup.find_all("h2")) > 0 else 0


def has_h3(soup):
    return 1 if len(soup.find_all("h3")) > 0 else 0


def has_footer(soup):
    return 1 if len(soup.find_all("footer")) > 0 else 0


def has_form(soup):
    return 1 if len(soup.find_all("form")) > 0 else 0


def has_text_area(soup):
    return 1 if len(soup.find_all("textarea")) > 0 else 0


def has_iframe(soup):
    return 1 if len(soup.find_all("iframe")) > 0 else 0


def has_text_input(soup):
    for tag in soup.find_all("input"):
        if tag.get("type") == "text":
            return 1
    return 0


def has_nav(soup):
    return 1 if len(soup.find_all("nav")) > 0 else 0


def has_object(soup):
    return 1 if len(soup.find_all("object")) > 0 else 0


def has_picture(soup):
    return 1 if len(soup.find_all("picture")) > 0 else 0


# QUANTITATIVE FEATURES (return counts / lengths)

def number_of_inputs(soup):
    return len(soup.find_all("input"))


def number_of_buttons(soup):
    return len(soup.find_all("button"))


def number_of_images(soup):
    image_tags = len(soup.find_all("image"))
    count = 0
    for meta in soup.find_all("meta"):
        if meta.get("type") or meta.get("name") == "image":
            count += 1
    return image_tags + count


def number_of_option(soup):
    return len(soup.find_all("option"))


def number_of_list(soup):
    return len(soup.find_all("li"))


def number_of_TH(soup):
    return len(soup.find_all("th"))


def number_of_TR(soup):
    return len(soup.find_all("tr"))


def number_of_href(soup):
    count = 0
    for link in soup.find_all("link"):
        if link.get("href"):
            count += 1
    return count


def number_of_paragraph(soup):
    return len(soup.find_all("p"))


def number_of_script(soup):
    return len(soup.find_all("script"))


def length_of_title(soup):
    if soup.title is None:
        return 0
    return len(soup.title.text)


def length_of_text(soup):
    return len(soup.get_text())


def number_of_clickable_button(soup):
    count = 0
    for button in soup.find_all("button"):
        if button.get("type") == "button":
            count += 1
    return count


def number_of_a(soup):
    return len(soup.find_all("a"))


def number_of_img(soup):
    return len(soup.find_all("img"))


def number_of_div(soup):
    return len(soup.find_all("div"))


def number_of_figure(soup):
    return len(soup.find_all("figure"))


def number_of_meta(soup):
    return len(soup.find_all("meta"))


def number_of_sources(soup):
    return len(soup.find_all("source"))


def number_of_span(soup):
    return len(soup.find_all("span"))


def number_of_table(soup):
    return len(soup.find_all("table"))


# LEXICAL FEATURES

def url_length(url):
    return len(url or "")


def qty_dots(url):
    return (url or "").count('.')


def qty_hyphens(url):
    return (url or "").count('-')


def has_ip_address(url):
    if not url:
        return 0

    parsed = urlparse(url)
    domain = (parsed.netloc or parsed.path).split(':')[0]
    if not domain:
        return 0

    ipv4_pattern = re.compile(r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$')
    match = ipv4_pattern.match(domain)
    if match and all(0 <= int(octet) <= 255 for octet in match.groups()):
        return 1
    return 0


def has_https(url):
    return 1 if isinstance(url, str) and url.startswith("https://") else 0

def create_vector(soup, url):
    return [
        has_title(soup),
        has_input(soup),
        has_button(soup),
        has_image(soup),
        has_submit(soup),
        has_link(soup),
        has_password(soup),
        has_email_input(soup),
        has_hidden_element(soup),
        has_audio(soup),
        has_video(soup),
        number_of_inputs(soup),
        number_of_buttons(soup),
        number_of_images(soup),
        number_of_option(soup),
        number_of_list(soup),
        number_of_TH(soup),
        number_of_TR(soup),
        number_of_href(soup),
        number_of_paragraph(soup),
        number_of_script(soup),
        length_of_title(soup),
        has_h1(soup),
        has_h2(soup),
        has_h3(soup),
        length_of_text(soup),
        number_of_clickable_button(soup),
        number_of_a(soup),
        number_of_img(soup),
        number_of_div(soup),
        number_of_figure(soup),
        has_footer(soup),
        has_form(soup),
        has_text_area(soup),
        has_iframe(soup),
        has_text_input(soup),
        number_of_meta(soup),
        has_nav(soup),
        has_object(soup),
        has_picture(soup),
        number_of_sources(soup),
        number_of_span(soup),
        number_of_table(soup),
        url_length(url),
        qty_dots(url),
        qty_hyphens(url),
        has_ip_address(url),
        has_https(url)
    ]