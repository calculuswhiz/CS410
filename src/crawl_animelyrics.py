#!/usr/bin/env python
# coding: utf-8

from os import mkdir, sep
from os.path import normpath, isdir
from time import sleep, time
from random import randint
import urllib2

# Where to save the output of all of the crawled pages.
DEFAULT_OUTPUT_PATH = normpath('../crawled/animelyrics/')

__doc__ = """Crawls Anime Lyrics dot Com for all of its pages.

http://www.animelyrics.com/
Saved pages are put in {} by default.
""".format(DEFAULT_OUTPUT_PATH)

HOME_PAGE = 'http://www.animelyrics.com/'

# All pages on the website we are crawling that index their content.
TOP_LEVEL_PAGES = [
'anime',
'jpop',
'game',
'dance',
'dancecd',
'doujin',
]

# How long to sleep between calls to the web site.
SLEEP_SEC_MIN = 1
SLEEP_SEC_MAX = 2

# Keep track of how long we have waited.
START_TIME = time()


def create_dir(path):
    """Creates the passed directory if it does not already exist."""
    if not isdir(normpath(path)):
        mkdir(normpath(path))


def get_page_content(url):
    """Sleeps, then gets the HTML page from a URL."""
    sleep(randint(SLEEP_SEC_MIN, SLEEP_SEC_MAX))
    page = urllib2.urlopen(url)
    content = page.read()
    return content


def retrieve_indices():
    """Accesses the web site's index pages and saves them locally."""
    for url in TOP_LEVEL_PAGES:
        try:
            content = get_page_content(''.join([HOME_PAGE, url, '/']))
        except URLError:
            print('Error: Could not retrieve URL {}'.format(url))
            # Skip the error and try reading the next URL.
            continue
        
        # Create the output's file name and its output path.
        filepath = normpath(''.join([DEFAULT_OUTPUT_PATH, sep, url, '.html']))
        with open(filepath, 'w') as outfile:
            outfile.write(content)


def main():
    create_dir('../crawled')
    create_dir(DEFAULT_OUTPUT_PATH)
    retrieve_indices()
    
    print('This script took {} seconds to run.'.format(time() - START_TIME))


if __name__ == '__main__':
    main()
