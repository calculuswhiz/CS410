#!/usr/bin/env python
# coding: utf-8

from os.path import normpath, isdir
from time import sleep, time
from random import randint
import urllib2

__doc__ = """Utilities and definitions for all of our codebase."""

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
