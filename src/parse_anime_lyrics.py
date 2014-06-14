#!/usr/bin/env python
# coding: utf-8

from os import listdir
from os.path import join as path_join
import re
from utils_and_defs import *
from bs4 import BeautifulSoup

__doc__ = """Collects all links from Anime Lyrics dot Com's Song Index pages."""

# Where to save the output of all of the crawled pages.


def get_song_list(filename, regex):
    """Gets a list of song URLs for Anime Lyrics from a song index page."""
    filename = path_join(DEFAULT_SONG_INDEX_PATH_AL, filename)
    with open(filename, 'r') as infile:
        alltext = infile.read()
    soup = BeautifulSoup(alltext)
    # Go inside of their layout table's first table-row.
    # Find all anchor tags with an "href" attribute.
    # Do not accept URLs for javascript (they use "#" in the URL).
    # Each link we want begins with "regex". eg. "anime/nichijou" for "anime".
    anchors = [anchor['href'] for anchor in soup.body.table.tr('a') \
        if anchor.has_attr('href') and '#' not in anchor['href'] and \
        anchor['href'].startswith(regex)]
    return anchors

def get_all_songs_from_index():
    """Gets a list of all song URLs from Anime Lyrics dot Com."""
    print('Parsing Anime Lyrics index files.')
    song_list = []
    # Get the list of URLs from the top index page.
    # These URLs point to albums of the form "anime/nichijou" under "anime".
    for filename in listdir(DEFAULT_SONG_INDEX_PATH_AL):
        song_list += get_song_list(filename, filename[:filename.find('.')])
    return song_list

main = get_all_songs_from_index

if __name__ == '__main__':
    main()
