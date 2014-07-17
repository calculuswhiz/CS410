#!/usr/bin/env python
# coding: utf-8

from os import listdir
from os.path import join as path_join
import re
from utils_and_defs import *
from bs4 import BeautifulSoup

__doc__ = """Gets all links from Anime Lyrics dot Com's pages.

Parsing can be done on the genre, album, and individual song pages.
Each type of page has a different function to be called for it.

Whether or not the parsing fails will depend on the parser used for
the BeautifulSoup library. Also, updates to the crawled site could
break this program.
"""

# When looking for the footer, this text will be looked for first.
ALBUM_LIST_START = 'Original Title'
# Find this substring and remove everything after it before caching.
FOOTER_TEXT = 'Submit a song'
# Find this substring and remove everything after it in a song page.
SONG_FOOTER_TEXT = 'Animelyrics.com now has an OpenSearch plugin'


def get_albums(fullpath, regex):
    """Gets a list of song URLs for Anime Lyrics from a song index page."""
    with open(fullpath, 'r') as infile:
        alltext = infile.read()
    soup = BeautifulSoup(alltext, BS_PARSER)
    # Go inside of their layout table's first table-row.
    # Find all anchor tags with an "href" attribute.
    # Do not accept URLs for javascript (they use "#" in the URL).
    # Each link begins with "regex". eg. "anime/nichijou" for "anime".
    # Anime Lyrics has bad links in their name that start with "del".
    #   Remove those links from our list.
    soup = soup.body.table.tr
    anchors = [anchor['href'] for anchor in soup('a') \
        if anchor.has_attr('href') and '#' not in anchor['href'] and \
        anchor['href'].startswith(regex) and \
        not anchor.contents[0].startswith('del')]
    return anchors

def remove_text_junk(text):
    """Removes the header and footer of Anime Lyrics album pages.
    
    Returns the a tuple of (processed_text, songs_found).
    On failure, processed_text is an empty string.
    """
    
    songs_found = True
    # Find the second h1 tag and save only up to that much.
    index_begin = text.find('<h1')
    if index_begin < 0:
        text = ''
    # Increment our find() result by one because otherwise we will
    # just hit our same h1 tag in the next search again.
    index_begin = text.find('<h1', index_begin + 1)
    if index_begin < 0:
        text = ''
    # Find the footer by searching for the list of albums.
    index_albums = text.find(ALBUM_LIST_START, index_begin)
    if index_albums < 0:
        text = ''
        songs_found = False
    # Find the footer by its tell-tale text beyond the album list.
    index_end = text.find(FOOTER_TEXT, index_albums)
    if index_end < 0:
        text = ''
    # Remove all unnecessary text.
    if index_begin >= 0 and index_end >= 0:
        text = text[index_begin : index_end]
    return (text, songs_found)

def remove_text_junk_from_song(text):
    """Removes the header and footer of Anime Lyrics song pages.
    
    Returns the processed text. On failure, returns an empty string.
    """
    
    # Find the second h1 tag and save only up to that much.
    index_begin = text.find('<h1')
    if index_begin < 0:
        text = ''
    # Increment our find() result by one because otherwise we will
    # just hit our same h1 tag in the next search again.
    index_begin = text.find('<h1', index_begin + 1)
    if index_begin < 0:
        text = ''
    # Find the footer by its tell-tale text beyond the album list.
    index_end = text.find(SONG_FOOTER_TEXT, index_begin)
    if index_end < 0:
        text = ''
    # This clears up a lot of unwanted text. Now we can do a reverse search
    # with less worries about processing time. Look for the song lyrics'
    # layout table closing tag.
    index_end = text.rfind('</table', index_begin, index_end)
    if index_end < 0:
        text = ''
    # Remove all unnecessary text.
    if index_begin >= 0 and index_end >= 0:
        text = text[index_begin : index_end]
    return text

def get_all_albums_from_index(quiet=True):
    """Gets a list of all song URLs from Anime Lyrics dot Com."""
    if not quiet:
        print('Fetching all album web pages from Anime Lyrics.')
    song_list = []
    # Get the list of URLs from the top index page.
    # URLs point to albums of the form "anime/nichijou" under "anime".
    for filename in listdir(DEFAULT_SONG_INDEX_PATH_AL):
        fullpath = normpath(path_join(DEFAULT_SONG_INDEX_PATH_AL,
            filename))
        song_list += get_albums(fullpath,
            filename[:filename.find('.')])
    if not quiet:
        print('Got {} album pages.'.format(len(song_list)))
    return song_list

def get_all_songs_from_albums(error_report, quiet=True):
    """Gets a list of all song URLs from an album page at Anime Lyrics."""
    print_errors = not quiet
    # This is a debugging/diagnostics variable. It does not affect the parsing.
    albums_crawled = 0
    urls = []
    genres = listdir(DEFAULT_OUTPUT_PATH_AL)
    # We do not want to parse our albums' index page. Just the albums.
    try:
        genres.remove('indices')
        genres.remove('songs.txt')
    except ValueError:
        pass
    
    for genre in genres:
        for album in listdir(path_join(DEFAULT_OUTPUT_PATH_AL, genre)):
            filename = normpath(path_join(DEFAULT_OUTPUT_PATH_AL, genre, album,
                'index.html'))
            albums_crawled += 1
            try:
                with open(filename, 'r') as infile:
                    content = infile.read()
            except IOError:
                # This file does not exist. Ignore it.
                error_report.add_error(
                    'Error reading album {}: {}. Maybe it does not exist?'.
                    format(albums_crawled, filename), also_print=print_errors)
                continue
            
            # The file was successfully loaded. Extract all anchor links.
            soup = BeautifulSoup(content)
            # Remove any anchors with # signs in them. They are for javascript.
            
            # Songs appear to have unique names so that they can reside in the
            # root folder of the album. That root folder has the index.html
            # which we are parsing *right now*, so do not save index.html URLs.
            # Also, URLs with '?' in them are for PHP pages that we do not want.
            anchors = [anchor['href'] for anchor in soup('a') \
                if anchor.has_attr('href') and '#' not in anchor['href'] and \
                '?' not in anchor['href'] and \
                'index.html' not in anchor['href']]
            urls += anchors
            
            if not quiet:
                if albums_crawled % DIAGNOSTICS_MULTIPLE == 0:
                    print('Album {}: {}'.format(albums_crawled, filename))
    if not quiet:
        print('Got {} song URLs from {} cached album pages.'.format(
            len(urls), albums_crawled))
    return urls

main = get_all_albums_from_index

if __name__ == '__main__':
    main()
