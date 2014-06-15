#!/usr/bin/env python
# coding: utf-8

from os import makedirs
from os.path import normpath, join as path_join
from time import sleep, time
from random import randint
import urllib2
from utils_and_defs import *
import parse_anime_lyrics

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


def save_url_locally(url, save_path):
    """Saves the passed URL locally.
    
    Returns True if the file was successfully saved. False otherwise.
    """
    
    try:
        content = get_page_content(url)
    except KeyboardInterrupt:
        return False
    
    if not content:
        # Failed to get the web page.
        return False
    
    # Create the output's file name and its output path.
    filepath = save_path
    with open(filepath, 'w') as outfile:
        outfile.write(content)
    return True

def retrieve_indices():
    """Accesses the web site's index pages and saves them locally."""
    for url in TOP_LEVEL_PAGES:
        try:
            save_url_locally(''.join([HOME_PAGE_AL, url, '/']),
                path_join(DEFAULT_SONG_INDEX_PATH_AL, url + '.html'))
        except KeyboardInterrupt:
            break

def retrieve_albums(relative_urls, quiet=True, max_retries=3):
    """Saves album pages from Anime Lyrics from the passed relative URLs.
    
    If you want to save a section of URLs, pass a slice of relative_urls.
    """
    
    debug_song_counter = 0
    for rel_url in relative_urls:
        create_dir_recursively(path_join(DEFAULT_OUTPUT_PATH_AL, rel_url))
        retry_count = max_retries
        success = False
        if not quiet:
            debug_song_counter += 1
            print('Fetching song {} of {}: {}'.format(
                debug_song_counter, len(relative_urls),
                ''.join([HOME_PAGE_AL, rel_url, '/'])))
        
        try:
            while not success and retry_count > 0:
                success = save_url_locally(''.join([HOME_PAGE_AL, rel_url, '/']),
                    path_join(DEFAULT_OUTPUT_PATH_AL, rel_url, 'index.html'))
                retry_count -= 1
        except KeyboardInterrupt:
            # Stop running the program.
            break
        
        if retry_count <= 0 and not success:
            print('Failed to fetch song: {}'.format(rel_url))

def main(quiet=True):
    if not quiet:
        print('Making output directories for Anime Lyrics.')
    create_dir_recursively(DEFAULT_OUTPUT_PATH_AL)
    create_dir_recursively(DEFAULT_SONG_INDEX_PATH_AL)
    if not quiet:
        print('Fetching all top level index pages (genres) from Anime Lyrics.')
    #retrieve_indices()
    # Save all of the pages from these URLs.
    if not quiet:
        print('Fetching all album web pages from Anime Lyrics.')
    song_list = parse_anime_lyrics.get_all_songs_from_index()
    #print(song_list[470:485]);return
    retrieve_albums(song_list, False)
    
    if not quiet:
        print('This script took {} seconds to run.'.format(time() - START_TIME))


if __name__ == '__main__':
    main(DEBUG_BE_QUIET)
