#!/usr/bin/env python
# coding: utf-8

from os import sep, listdir
from os.path import normpath
import re
from utils_and_defs import *
from bs4 import BeautifulSoup

__doc__ = """Collects all links from Anime Lyrics dot Com's Song Index pages."""

# Where to save the output of all of the crawled pages.
DEFAULT_OUTPUT_PATH = normpath('../crawled/animelyrics/')
DEFAULT_SONG_INDEX_PATH = normpath(DEFAULT_OUTPUT_PATH + sep + 'indices/')


def crop_index_content(alltext):
    """Removes extraneous information around the list of songs."""
    pass

def get_song_list(filename, regex):
    """Gets a list of song URLs for Anime Lyrics from a song index page."""
    soup = BeautifulSoup(filename)
    # Go inside of their layout table's layout table's first table-row.
    # Yes, they have nested layout tables.
    soup = soup.body.table.table.tr
    # Find all anchor tags.
    anchors = soup('a')
    anchors = [anchor['href'] for anchor in anchors]

def main():
    print('Ready to parse Anime Lyrics index files.')
    for filename in listdir(DEFAULT_SONG_INDEX_PATH):
        print(filename)
    get_song_list('anime.html', 'anime')

if __name__ == '__main__':
    main()
