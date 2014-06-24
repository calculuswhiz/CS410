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
    
    Returns the processed text on success or an empty string otherwise.
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
    # Find the footer by searching for the list of albums.
    index_albums = text.find(ALBUM_LIST_START, index_begin)
    if index_albums < 0:
        text = ''
    # Find the footer by its tell-tale text beyond the album list.
    index_end = text.find(FOOTER_TEXT, index_albums)
    if index_end < 0:
        text = ''
    # Remove all unnecessary text.
    if index_begin >= 0 and index_end >= 0:
        text = text[index_begin : index_end]
    return text

def get_all_songs_from_index(quiet=True):
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

main = get_all_songs_from_index

if __name__ == '__main__':
    main()
