#!/usr/bin/env python
# coding: utf-8

from os import makedirs
from os.path import normpath, isdir, join as path_join
from time import sleep, time
from random import randint
import re
import urllib2

__doc__ = """Utilities and definitions for all of our codebase."""

# Whether or not to print output.
DEBUG_BE_QUIET = False

# How long to sleep between calls to the web site.
SLEEP_SEC_MIN = 1
SLEEP_SEC_MAX = 2

# Keep track of how long we have waited.
START_TIME = time()

# URL and directory constants for Anime Lyrics dot Com (AL).
HOME_PAGE_AL = 'http://www.animelyrics.com/'
DEFAULT_OUTPUT_PATH_AL = normpath('../crawled/animelyrics/')
DEFAULT_SONG_INDEX_PATH_AL = path_join(DEFAULT_OUTPUT_PATH_AL, 'indices/')
SONGS_LIST_FILEPATH = normpath(path_join(DEFAULT_OUTPUT_PATH_AL, 'songs.txt'))

# The parser that BeautifulSoup will use for reading the web pages.
# http://www.crummy.com/software/BeautifulSoup/bs4/doc/#parser-installation
BS_PARSER = 'lxml'

# The regex that looks for the meta tag which states the file encoding.
charset_regex = re.compile('<meta .*charset=.*>',
    re.UNICODE | re.IGNORECASE)

# How often to display diagnostics. Using a counter, use the modulus on it.
# Usage: if counter % DIAGNOSTICS_MULTIPLE == 0:
#    print('{}: Doing stuff.'.format(counter))
DIAGNOSTICS_MULTIPLE = 500
# This is the same, but applies to URLs we are fetching.
DIAGNOSTICS_URL_MULTIPLE = 10

# Keep track of all errors and write them out when the program ends.
class ErrorReport(object):
    """Stores all errors that occurred and writes them to disk."""
    
    def __init__(my):
        my.report = ''
    
    def add_error(my, text, also_print=False):
        """Adds a line of text to the error report."""
        my.report += text + '\n'
        if also_print:
            print(text.strip())
    
    def write_out(my, filename='error.log'):
        """Writes the error report out to disk if there were errors."""
        if my.report:
            with open(filename, 'w') as error_file:
                error_file.write(my.report)

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
    except urllib2.URLError:
        print('Error: Could not retrieve URL {}'.format(url))
    except KeyboardInterrupt:
        print('Forced termination by keyboard input.')
        # Tell the caller to stop running.
        raise
    except:
        from sys import exc_info
        print('Unexpected error:', exc_info()[0])
    return content

def extract_meta_charset_tag(text):
    """Looks for and extracts the <meta ... charset=""> text.
    
    It should look like the following form.
    <META http-equiv="Content-Type" content="text/html; charset=UTF-8">
    Saving this text is important for knowing the file encoding.
    
    Returns the meta tag on success or an empty string on failure.
    """
    
    meta_tag = ''
    match = charset_regex.search(text)
    if match:
        meta_tag = text[match.start() : match.end()]
    return meta_tag
