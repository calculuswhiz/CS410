#!/usr/bin/env python
# coding: utf-8

from os import makedirs, listdir
from os.path import normpath, isdir, pardir, join as path_join, sep as path_sep
from time import sleep, time
from random import randint
try:
    # Import regex which will be supported in the future.
    import regex as re
except ImportError:
    # Import re which regex will replace. Maybe it will just work?
    import re
    print('Warning: Unable to import "regex".')
    print('If this program crashes, get the "regex" module for Python.')
import urllib2

__doc__ = """Utilities and definitions for all of our codebase."""

# Whether or not to print output.
DEBUG_PRINT_DIAGNOSTICS = True

# How long to sleep between calls to the web site.
SLEEP_SEC_MIN = 1
SLEEP_SEC_MAX = 2

# Keep track of how long we have waited.
START_TIME = time()

# URL and directory constants for Anime Lyrics dot Com (AL).
HOME_PAGE_AL = 'http://www.animelyrics.com/'
DEFAULT_OUTPUT_PATH_AL = normpath('../../crawled/animelyrics/')
DEFAULT_SONG_INDEX_PATH_AL = path_join(DEFAULT_OUTPUT_PATH_AL, 'indices/')
SONGS_LIST_FILEPATH = normpath(path_join(DEFAULT_OUTPUT_PATH_AL, 'songs.txt'))
OUTPUT_PATH_AL_INDEXABLE = normpath('../../indexable/animelyrics/')
DOC_LIST_FILENAME = normpath('../../indexable/docs.txt')
# Where the parent directories are. Used to back reference where crawled and
# indexable directories are by using crawled_file[ABOVE_CRAWLED_DIR:]
PARENT_DIRS = ''.join([pardir, path_sep, pardir, path_sep])
ABOVE_CRAWLED_DIR = len(PARENT_DIRS) + len('crawled') + len(path_sep)

# The parser that BeautifulSoup will use for reading the web pages.
# http://www.crummy.com/software/BeautifulSoup/bs4/doc/#parser-installation
BS_PARSER = 'lxml'

# The regex that looks for the meta tag which states the file encoding.
charset_regex = re.compile('<meta .*charset=.*>',
    re.UNICODE | re.IGNORECASE)
# The regex string that looks for Japanese text. Specifically, any hiragana,
# katakana, or kanji character.
# Note: \u4e00-\u9faf is the range of kanji. \u3005 is the kanji repeater: 々.
# \W means any non-alphanumeric char.
# http://www.rikai.com/library/kanjitables/kanji_codes.unicode.shtml
RE_JAPANESE_GLYPH = '[\p{Hiragana}\p{Katakana}\u4e00-\u9faf\W\u3005]'
# The regex that looks for Japanese characters that are separated by whitespace.
# For example, it will look for "き キ" or "今     は" and such.
spaced_jp_regex = re.compile(RE_JAPANESE_GLYPH + '\s+' + RE_JAPANESE_GLYPH,
    re.UNICODE)
# This is the function that goes along with the above regex during substitution.
def remove_inner_spaces(m):
    """Removes a MatchObject's space between the first and last characters."""
    return m.group(0)[0] + m.group(0)[-1]

# How often to display diagnostics. Using a counter, use the modulus on it.
# Usage: if counter % DIAGNOSTICS_MULTIPLE == 0:
#    print('{}: Doing stuff.'.format(counter))
DIAGNOSTICS_MULTIPLE = 500
# This is the same, but applies to URLs we are fetching.
DIAGNOSTICS_URL_MULTIPLE = 1

# All pages on the website we are crawling that index their content.
TOP_LEVEL_PAGES = [
'anime',
'jpop',
'game',
'dance',
'dancecd',
'doujin',
]

# Keep track of all errors and write them out when the program ends.
class ErrorReport(object):
    """Stores all errors that occurred and writes them to disk."""
    
    def __init__(my):
        my._report = ''
        # Whether or not to print the errors as they are added.
        my._print_errors = DEBUG_PRINT_DIAGNOSTICS
    
    def set_print_errors(my, set_errors):
        """Sets whether or not to print out errors when added."""
        my._print_errors = set_errors
    
    def get_suitable_report_filename(my):
        """Chooses a filename to avoid conflicts between error log filenames.
        
        Error logs have a name like error0000.log and will increment the
        number if the file already exists. If error9999.log exists, then
        error0000.log will be written in to. Please clean up the error logs
        if this happens.
        """
        
        error_log_number = 0
        error_files = [filename for filename in listdir('.') \
            if 'error' in filename]
        error_files.sort()
        if len(error_files) > 0:
            # Try to increment the number of the last error report's filename.
            try:
                error_log_number = int(error_files[-1][5:9]) + 1
            except ValueError:
                # It's not the report filename we expected. Let's just use 0.
                pass
        # Avoid underflow and overflow.
        if error_log_number > 9999 or error_log_number < 0:
            error_log_number = 0
        return 'error{:0>4}.log'.format(error_log_number)
    
    def add_error(my, text):
        """Adds a line of text to the error report."""
        my._report += text + '\n'
        if my._print_errors:
            print(text.strip())
    
    def write_out(my, filename='error.log'):
        """Writes the error report out to disk if there were errors."""
        if my._report:
            with open(filename, 'w') as error_file:
                error_file.write(my._report)

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
