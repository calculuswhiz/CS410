#!/usr/bin/env python
# coding: utf-8

from os import makedirs
from os.path import normpath, isfile, join as path_join
from time import sleep, time
from random import randint
import urllib2
from utils_and_defs import *
import parse_anime_lyrics
from bs4 import BeautifulSoup

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
                normpath(path_join(DEFAULT_SONG_INDEX_PATH_AL,
                    url + '.html')))
        except KeyboardInterrupt:
            break

def retrieve_albums(relative_urls, quiet=True, max_retries=3):
    """Saves album pages from Anime Lyrics from the passed relative URLs.
    
    If you want to save a section of URLs, pass a slice of relative_urls.
    """
    
    if not quiet:
        print('Fetching all top level index pages (genres) from Anime Lyrics.')
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
                success = save_url_locally(''.join(
                    [HOME_PAGE_AL, rel_url, '/']),
                    normpath(path_join(DEFAULT_OUTPUT_PATH_AL, rel_url,
                    'index.html')))
                retry_count -= 1
        except KeyboardInterrupt:
            # Stop running the program.
            break
        
        if retry_count <= 0 and not success:
            print('Failed to fetch song: {}'.format(rel_url))

def trim_local_album_pages():
    """Removes junk from album pages and saves them in nice.html
    
    This is a one-time use function that will trim every crawled
    album page stored on disk.
    """
    
    from os import listdir
    from os.path import isfile
    
    for genre in TOP_LEVEL_PAGES:
        genre_path = normpath(path_join(DEFAULT_OUTPUT_PATH_AL, genre))
        for album in listdir(genre_path):
            fullpath = normpath(path_join(
                genre_path, album, 'index.html'))
            if not isfile(fullpath):
                error = 'File does not exist: {}.'.format(fullpath)
                continue
            
            with open(fullpath, 'r') as infile:
                text = infile.read()
            trimmed_text = parse_anime_lyrics.remove_text_junk(text)
            if trimmed_text:
                nicepath = normpath(path_join(
                    genre_path, album, 'nice.html'))
                soup = BeautifulSoup(trimmed_text)
                with open(nicepath, 'w') as outfile:
                    outfile.write(soup.prettify('utf-8'))
            else:
                error = 'Failed to trim {}.'.format(fullpath)
                print(error)
                global full_error_report
                full_error_report += '\n' + error

def main(quiet=True):
    try:
        if not quiet:
            print('Making output directories for Anime Lyrics.')
        create_dir_recursively(DEFAULT_OUTPUT_PATH_AL)
        create_dir_recursively(DEFAULT_SONG_INDEX_PATH_AL)\
        #retrieve_indices()
        #song_list = parse_anime_lyrics.get_all_songs_from_index()
        #retrieve_albums(song_list, False)
        trim_local_album_pages()
    except KeyboardInterrupt:
        pass
    except:
        from sys import exc_info
        global full_error_report
        full_error_report += '\nUnexpected error: {}\n{}\n{}\n'.format(
            exc_info()[0], exc_info()[1], exc_info()[2])
        if full_error_report:
            with open('error.log', 'w') as error_file:
                error_file.write(full_error_report)
        print('An error occured. Please read error.log.')
        raise
    finally:
        if not quiet:
            print('This script took {} seconds to run.'.format(
                time() - START_TIME))


if __name__ == '__main__':
    main(DEBUG_BE_QUIET)
