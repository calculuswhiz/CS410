#!/usr/bin/env python
# coding: utf-8

from os import makedirs
from os.path import normpath, join as path_join
from time import sleep, time
from random import randint
import urllib2
from utils_and_defs import *
import parse_anime_lyrics

# Where to save the output of all of the crawled pages.
DEFAULT_OUTPUT_PATH = normpath('../crawled/animelyrics/')
DEFAULT_SONG_INDEX_PATH = path_join(DEFAULT_OUTPUT_PATH, 'indices/')

__doc__ = """Crawls Anime Lyrics dot Com for all of its pages.

http://www.animelyrics.com/
Saved pages are put in {} by default.
""".format(DEFAULT_OUTPUT_PATH_AL)

# All pages on the website we are crawling that index their content.
TOP_LEVEL_PAGES = [
'anime',
'jpop',
'game',
'dance',
'dancecd',
'doujin',
]


def retrieve_indices():
    """Accesses the web site's index pages and saves them locally."""
    for url in TOP_LEVEL_PAGES:
        try:
            content = get_page_content(''.join([HOME_PAGE_AL, url, '/']))
        except KeyboardInterrupt:
            break
        
        # Create the output's file name and its output path.
        filepath = path_join(DEFAULT_SONG_INDEX_PATH_AL, url + '.html')
        with open(filepath, 'w') as outfile:
            outfile.write(content)


def main():
    print('Making output directories for Anime Lyrics.')
    create_dir_recursively(DEFAULT_OUTPUT_PATH_AL)
    create_dir_recursively(DEFAULT_SONG_INDEX_PATH_AL)
    print('Fetching all top level index pages (genres) from Anime Lyrics.')
    retrieve_indices()
    # Save all of the pages from these URLs.
    print('Fetching all album web pages from Anime Lyrics.')
    song_list = parse_anime_lyrics.get_all_songs_from_index()
    
    print('This script took {} seconds to run.'.format(time() - START_TIME))


if __name__ == '__main__':
    main()
