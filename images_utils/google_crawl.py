
# requires: selenium, chromium-driver, retry
# Thanks to `Sam Watkins` on stackoverflow for this file. :)
# https://stackoverflow.com/users/218294/sam-watkins
# https://stackoverflow.com/questions/20716842/python-download-images-from-google-image-search/61982397#61982397?newreg=1c27b159a6a44bd08ae95ddbcf083ae1

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import selenium.common.exceptions as sel_ex
import sys
import time
import urllib.parse
from retry import retry
import argparse
import logging

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger()
retry_logger = None

css_thumbnail = "img.Q4LuWd"
css_large = "img.n3VNCb"
css_load_more = ".mye4qd"
selenium_exceptions = (
    sel_ex.ElementClickInterceptedException,
    sel_ex.ElementNotInteractableException,
    sel_ex.StaleElementReferenceException,
)


def scroll_to_end(wd):
    wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")


@retry(exceptions=KeyError, tries=6, delay=0.1, backoff=2, logger=retry_logger)
def get_thumbnails(wd, want_more_than=0):
    wd.execute_script("document.querySelector('{}').click();".format(css_load_more))
    thumbnails = wd.find_elements_by_css_selector(css_thumbnail)
    n_results = len(thumbnails)
    if n_results <= want_more_than:
        raise KeyError("no new thumbnails")
    return thumbnails


@retry(exceptions=KeyError, tries=6, delay=0.1, backoff=2, logger=retry_logger)
def get_image_src(wd):
    actual_images = wd.find_elements_by_css_selector(css_large)
    sources = []
    for img in actual_images:
        src = img.get_attribute("src")
        if src.startswith("http") and not src.startswith(
            "https://encrypted-tbn0.gstatic.com/"
        ):
            sources.append(src)
    if not len(sources):
        raise KeyError("no large image")
    return sources


@retry(
    exceptions=selenium_exceptions, tries=6, delay=0.1, backoff=2, logger=retry_logger
)
def retry_click(el):
    el.click()


def get_images(wd, start=0, n=20, out=None):
    thumbnails = []
    count = len(thumbnails)
    while count < n:
        scroll_to_end(wd)
        try:
            thumbnails = get_thumbnails(wd, want_more_than=count)
        except KeyError as e:
            logger.warning("cannot load enough thumbnails")
            break
        count = len(thumbnails)
    sources = []
    for tn in thumbnails:
        try:
            retry_click(tn)
        except selenium_exceptions as e:
            logger.warning("main image click failed")
            continue
        sources1 = []
        try:
            sources1 = get_image_src(wd)
        except KeyError as e:
            pass
            # logger.warning("main image not found")
        if not sources1:
            tn_src = tn.get_attribute("src")
            if not tn_src.startswith("data"):
                logger.warning("no src found for main image, using thumbnail")
                sources1 = [tn_src]
            else:
                logger.warning("no src found for main image, thumbnail is a data URL")
        for src in sources1:
            if not src in sources:
                sources.append(src)
                if out:
                    print(src, file=out)
                    out.flush()
        if len(sources) >= n:
            break
    return sources


def google_image_search(wd, query, safe="off", n=20, opts="", out=None):
    search_url_t = "https://www.google.com/search?safe={safe}&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img&tbs={opts}"
    search_url = search_url_t.format(
        q=urllib.parse.quote(query), opts=urllib.parse.quote(opts), safe=safe
    )
    wd.get(search_url)
    sources = get_images(wd, n=n, out=out)
    return sources


def run_search(query, safe, n, otions, out=None):
    opts = Options()
    opts.add_argument("--headless")
    
    with webdriver.Chrome(ChromeDriverManager().install(), options=opts) as wd:
        sources = google_image_search(
            wd, query, safe=safe, n=n, opts=otions, out=None
        )
    return sources