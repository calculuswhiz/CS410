#!/usr/bin/env python
# coding: utf-8

from os import makedirs
from os.path import normpath, isdir, join as path_join
from time import sleep, time
from random import randint
import urllib2

__doc__ = """Utilities and definitions for all of our codebase."""

# How long to sleep between calls to the web site.
SLEEP_SEC_MIN = 1
SLEEP_SEC_MAX = 2

# Keep track of how long we have waited.
START_TIME = time()

# URL and directory constants for Anime Lyrics dot Com (AL).
HOME_PAGE_AL = 'http://www.animelyrics.com/'
DEFAULT_OUTPUT_PATH_AL = normpath('../crawled/animelyrics/')
DEFAULT_SONG_INDEX_PATH_AL = path_join(DEFAULT_OUTPUT_PATH_AL, 'indices/')


def create_dir_recursively(path):
    """Creates the passed directory if it does not already exist."""
    try:
        makedirs(path)
    except OSError:
        pass


def get_page_content(url):
    """Sleeps, then gets the HTML page from a URL."""
    content = None
    try:
        sleep(randint(SLEEP_SEC_MIN, SLEEP_SEC_MAX))
        page = urllib2.urlopen(url)
        content = page.read()
    except URLError:
        print('Error: Could not retrieve URL {}'.format(url))
    except KeyboardInterrupt:
        print('Forced termination by keyboard input.')
        # Tell the caller to stop running.
        raise
    except:
        from sys import exc_info
        print('Unexpected error:', exc_info()[0])
    return content
