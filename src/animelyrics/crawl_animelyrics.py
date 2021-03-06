#!/usr/bin/env python
# coding: utf-8

from sys import argv
from os import makedirs
from os.path import normpath, isfile, dirname, join as path_join
from time import sleep, time
from random import randint
import urllib2
import argparse
from utils_and_defs import *
import parse_anime_lyrics
from bs4 import BeautifulSoup

__doc__ = """Crawls Anime Lyrics dot Com for all of its pages.

http://www.animelyrics.com/
Saved pages are put in {} by default.
""".format(DEFAULT_OUTPUT_PATH_AL)


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

def retrieve_albums(relative_urls, error_report, max_retries=3):
    """Saves album pages from Anime Lyrics from relative_urls.
    
    Each page is saved in index.html after being trimmed.
    If you want to save a section of URLs, slice relative_urls.
    """
    
    if DEBUG_PRINT_DIAGNOSTICS:
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
            if debug_song_counter % DIAGNOSTIC_MULTIPLE == 0:
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
            error_report.add_error('Failed to fetch song: {}'.format(rel_url))
        else:
            fullpath = normpath(path_join(
                DEFAULT_OUTPUT_PATH_AL, rel_url, 'index.html'))
            nicepath = normpath(path_join(output_path, 'index.html'))
            # Trim the content.
            save_page_with_proper_markup(text, trim_album, fullpath, nicepath,
                error_report, print_errors)

def save_page_with_proper_markup(text, trim_func, inputpath, outputpath,
    error_report):
    """Takes plain text markup and resaves it as valid HTML markup."""
    # Trim the content.
    trimmed_text = trim_func(text, inputpath, error_report)
    if trimmed_text:
        text = trimmed_text
    soup = BeautifulSoup(text)
    # Save the cleaned up page locally.
    with open(outputpath, 'w') as outfile:
        outfile.write(soup.prettify('utf-8'))

def retrieve_songs(song_paths, error_report, max_retries=3):
    """Saves song pages from Anime Lyrics from song_paths.
    
    Saves all online pages from Anime Lyrics produced by song_paths.
    song_paths are paths such as "anime/keion/myownroad.txt".
    """
    
    if DEBUG_PRINT_DIAGNOSTICS:
        print('Fetching Anime Lyrics song pages.')
    debug_song_counter = 0
    for rel_path in song_paths:
        output_path = path_join(DEFAULT_OUTPUT_PATH_AL, rel_path)
        create_dir_recursively(dirname(output_path))
        url_path = ''.join([HOME_PAGE_AL, rel_path])
        retry_count = max_retries
        success = False
        if not quiet:
            debug_song_counter += 1
            if debug_song_counter % DIAGNOSTICS_URL_MULTIPLE == 0:
                print('Fetching song {} of {}: {}'.format(
                    debug_song_counter, len(song_paths),
                    url_path))
        
        try:
            while not success and retry_count > 0:
                text = get_page_content(url_path)
                success = text is not None
                retry_count -= 1
        except KeyboardInterrupt:
            # Stop running the program.
            break
        
        if retry_count <= 0 and not success:
            error_report.add_error('Failed to fetch song {}: {}'.format(
                debug_song_counter, rel_path))
        else:
            # Trim the content.
            save_page_with_proper_markup(text, trim_song, output_path,
                output_path, error_report)

def trim_album(text, fullpath, error_report):
    """Returns the album page with unwanted text removed from it.
    
    @param text: All of the web page's text as one string.
    
    Returns the processed text on success or an empty string otherwise.
    """
    
    trimmed_text = ''
    if not text:
        # This is an empty file. Do not parse it.
        error_report.add_error(
            'File is empty: {}.'.format(fullpath))
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
            'Failed to extract the charset of {}.'.format(
            fullpath))
    
    if trimmed_text or (not trimmed_text and not songs_found):
        if not songs_found:
            # Trim the page despite having no songs.
            # Make a warning in the error log.
            error_report.add_error(
                'Trimmed a songless page: {}.'.format(
                fullpath))
        
        # We have successfully trimmed the text.
        if charset_tag:
            # Add the meta tag if we have it.
            trimmed_text = '\n'.join([charset_tag,trimmed_text])
    else:
        # Trimming the text failed. Output an error report.
        error_report.add_error(
            'Failed to trim {}.'.format(fullpath))
    
    return trimmed_text

def trim_song(text, fullpath, error_report):
    """Returns the song page with unwanted text removed from it.
    
    @param text: All of the web page's text as one string.
    
    Returns the processed text on success or an empty string otherwise.
    """
    
    trimmed_text = ''
    if not text:
        # This is an empty file. Do not parse it.
        error_report.add_error(
            'File is empty: {}.'.format(fullpath))
        return trimmed_text

    charset_tag = extract_meta_charset_tag(text)
    if not charset_tag:
        # The meta tag is not important, so we will continue.
        # Log the failure anyways.
        error_report.add_error(
            'Failed to extract the charset of {}.'.format(
            fullpath))
    
    trimmed_text = parse_anime_lyrics.remove_text_junk_from_song(text)
    charset_tag = extract_meta_charset_tag(text)
    if not trimmed_text:
        error_report.add_error(
            'Failed to trim: {}.'.format(fullpath))
    elif charset_tag:
        trimmed_text = '\n'.join([charset_tag,trimmed_text])
    
    return trimmed_text

def write_song_paths_to_file(paths):
    """Writes all song URLs to a file for later access."""
    with open(SONGS_LIST_FILEPATH, 'w') as outfile:
        outfile.write('\n'.join(paths))

def read_song_paths_from_file(filename):
    """Writes all song URLs to a file for later access."""
    paths = []
    with open(filename, 'r') as infile:
        paths = [line.strip() for line in infile.readlines()]
    return paths

def main():
    error_report = ErrorReport()
    try:
        if DEBUG_PRINT_DIAGNOSTICS:
            print('Making output directories for Anime Lyrics.')
        #create_dir_recursively(DEFAULT_OUTPUT_PATH_AL)
        #create_dir_recursively(DEFAULT_SONG_INDEX_PATH_AL)
        #retrieve_indices()
        #song_list = parse_anime_lyrics.get_all_albums_from_index()
        #retrieve_albums(song_list, error_report)
        #paths = parse_anime_lyrics.get_all_songs_from_albums(error_report)
        #write_song_paths_to_file(paths)
        if isfile('test.html'):
            # Do a simple test to see if we can successfully trim a song.
            with open('test.html', 'r') as infile:
                text = infile.read()
            save_page_with_proper_markup(text, trim_song, 'test.html',
                'out.html', error_report)
        #"""
        paths = read_song_paths_from_file(SONGS_LIST_FILEPATH)
        if len(argv) == 3:
            retrieve_songs(paths[int(argv[1]):int(argv[2])],
                error_report)
        else:
            print('Arguments: paths_start, paths_end')
        #"""
    except KeyboardInterrupt:
        pass
    except:
        from sys import exc_info
        error_report.add_error(
            'Unexpected error of type {}\n{}\n{}'.format(
            exc_info()[0], exc_info()[1], exc_info()[2]))
        raise
    finally:
        error_filename = error_report.get_suitable_report_filename()
        error_report.write_out(error_filename)
        if DEBUG_PRINT_DIAGNOSTICS:
            print('This script took {:.2f} seconds to run.'.format(
                time() - START_TIME))


if __name__ == '__main__':
    main()
