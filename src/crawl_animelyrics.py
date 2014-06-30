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

def retrieve_albums(relative_urls, error_report, quiet=True, max_retries=3):
    """Saves album pages from Anime Lyrics from relative_urls.
    
    Each page is saved in index.html after being trimmed.
    If you want to save a section of URLs, slice relative_urls.
    """
    
    print_errors = not quiet
    if not quiet:
        print('Fetching Anime Lyrics top level index pages (genres).')
    debug_song_counter = 0
    for rel_url in relative_urls:
        output_path = path_join(DEFAULT_OUTPUT_PATH_AL, rel_url)
        create_dir_recursively(output_path)
        url = ''.join([HOME_PAGE_AL, rel_url, '/'])
        retry_count = max_retries
        success = False
        if not quiet:
            debug_song_counter += 1
            print('Fetching song {} of {}: {}'.format(
                debug_song_counter, len(relative_urls),
                ''.join([HOME_PAGE_AL, rel_url, '/'])))
        
        try:
            while not success and retry_count > 0:
                text = get_page_content(url)
                success = text is not None
                retry_count -= 1
        except KeyboardInterrupt:
            # Stop running the program.
            break
        
        if retry_count <= 0 and not success:
            print('Failed to fetch song: {}'.format(rel_url))
        else:
            fullpath = normpath(path_join(
                DEFAULT_OUTPUT_PATH_AL, rel_url, 'index.html'))
            # Trim the content.
            trimmed_text = trim_album(text, fullpath, error_report,
                print_errors)
            if trimmed_text:
                text = trimmed_text
            soup = BeautifulSoup(text)
            # Save the cleaned up page locally.
            nicepath = normpath(path_join(output_path, 'index.html'))
            with open(nicepath, 'w') as outfile:
                outfile.write(soup.prettify('utf-8'))

def trim_album(text, fullpath, error_report, quiet=True):
    """Returns the album page with unwanted text removed from it.
    
    @param text: All of the web page's text as one string.
    
    Returns the processed text on success or an empty string otherwise.
    """
    
    print_errors = not quiet
    trimmed_text = ''
    if not text:
        # This is an empty file. Do not parse it.
        error_report.add_error(
            'File is empty: {}.\n'.format(fullpath),
            also_print=print_errors)
        return trimmed_text
    
    charset_tag = extract_meta_charset_tag(text)
    if charset_tag:
        # Got the meta tag, so trim out more unwanted text.
        trimmed_text, songs_found = \
            parse_anime_lyrics.remove_text_junk(text)
    else:
        # The meta tag is not important, so we will continue.
        # Log the failure anyways.
        error_report.add_error(
            'Failed to extract the charset of {}.\n'.format(
            fullpath), also_print=print_errors)
    
    if trimmed_text or (not trimmed_text and not songs_found):
        if not songs_found:
            # Trim the page despite having no songs.
            # Make a warning in the error log.
            error_report.add_error(
                'Trimmed a songless page: {}.\n'.format(
                fullpath), also_print=print_errors)
        
        # We have successfully trimmed the text.
        if charset_tag:
            # Add the meta tag if we have it.
            trimmed_text = '\n'.join([charset_tag,trimmed_text])
    else:
        # Trimming the text failed. Output an error report.
        error_report.add_error(
            'Failed to trim {}.\n'.format(fullpath),
            also_print=print_errors)
    
    return trimmed_text

def trim_local_album_pages(error_report, quiet=True):
    """Removes junk from album pages and saves them in nice.html
    
    This is a one-time use function that will trim every crawled
    album page stored on disk.
    """
    
    from os import listdir
    from os.path import isfile
    
    print_errors = not quiet
    # Loop through all of Anime Lyrics' genres to produce path names.
    for genre in TOP_LEVEL_PAGES:
        genre_path = normpath(path_join(DEFAULT_OUTPUT_PATH_AL, genre))
        # Loop through all albums that exist in each genre.
        for album in listdir(genre_path):
            # Get the album web page stored as index.html .
            fullpath = normpath(path_join(
                genre_path, album, 'index.html'))
            if not isfile(fullpath):
                error_report.add_error(
                    'File does not exist: {}.\n'.format(fullpath),
                    also_print=print_errors)
                continue
            
            with open(fullpath, 'r') as infile:
                text = infile.read()
            text = trim_album(text, fullpath, error_report,
                print_errors)
            if text:
                soup = BeautifulSoup(text)
                # Save the cleaned up page locally.
                nicepath = normpath(path_join(
                    genre_path, album, 'nice.html'))
                with open(nicepath, 'w') as outfile:
                    outfile.write(soup.prettify('utf-8'))

def main(quiet=True):
    error_report = ErrorReport()
    try:
        if not quiet:
            print('Making output directories for Anime Lyrics.')
        create_dir_recursively(DEFAULT_OUTPUT_PATH_AL)
        create_dir_recursively(DEFAULT_SONG_INDEX_PATH_AL)\
        #retrieve_indices()
        song_list = parse_anime_lyrics.get_all_songs_from_index()
        retrieve_albums(song_list, error_report, quiet)
        #trim_local_album_pages(error_report, quiet)
    except KeyboardInterrupt:
        pass
    except:
        from sys import exc_info
        error_report.add_error(
            'Unexpected error of type {}\n{}\n{}\n'.format(
            exc_info()[0], exc_info()[1], exc_info()[2]),
            also_print=False)
        raise
    finally:
        error_report.write_out()
        if not quiet:
            print('This script took {} seconds to run.'.format(
                time() - START_TIME))


if __name__ == '__main__':
    main(DEBUG_BE_QUIET)
