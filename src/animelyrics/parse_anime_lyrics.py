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
# Whether we should save HTML pages or Print-Preview pages.
SAVE_HTML_VARIANT = True


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
    index_true_end = text.rfind('</table', index_begin, index_end)
    if index_true_end >= 0:
        # Songs without translations on Anime Lyrics do not
        # have layout tables surrounding their lyrics, so take out
        # more text if we have spotted the layout table.
        index_end = index_true_end
    # Remove all unnecessary text.
    if index_begin >= 0 and index_end >= 0:
        text = text[index_begin : index_end]
    return text

def get_all_albums_from_index():
    """Gets a list of all song URLs from Anime Lyrics dot Com."""
    if DEBUG_PRINT_DIAGNOSTICS:
        print('Fetching all album web pages from Anime Lyrics.')
    song_list = []
    # Get the list of URLs from the top index page.
    # URLs point to albums of the form "anime/nichijou" under "anime".
    for filename in listdir(DEFAULT_SONG_INDEX_PATH_AL):
        fullpath = normpath(path_join(DEFAULT_SONG_INDEX_PATH_AL,
            filename))
        song_list += get_albums(fullpath,
            filename[:filename.find('.')])
    if DEBUG_PRINT_DIAGNOSTICS:
        print('Got {} album pages.'.format(len(song_list)))
    return song_list

def does_song_have_kanji_lyrics(soup_song, error_report):
    """Checks if a song found in the soup has kanji lyrics available.
    
    It does this by looking at where the anchor link of the song was found.
    The parent of the song's anchor may have images. One image may have the
    alt text "Japanese Kanji available". If that is found, this function
    returns True.
    """
    
    return len(soup_song.parent('img', alt='Japanese Kanji available')) > 0

def is_anchor_in_song_field(soup_song, error_report):
    """Checks if a song we found is actually in the table Description field.
    
    Songs in this section are not what we want to fetch. It is found by looking
    for the parent of the passed anchor, then checking if its class is "alt".
    Note that the class we DO want to store is "specalt".
    
    @returns: True if the anchor is in the description field of the table.
    """
    
    try:
        return soup_song.parent['class'][0] == 'specalt'
    except KeyError:
        # The parent tag doesn't have a class defined. Our rule doesn't apply.
        return False

def is_song_valid_url(soup_anchor, error_report):
    """Checks if a song's anchor is a valid URL.
    
    index pages are ignored because they are album pages instead of song pages.
    "&lt;a" which is "<a" links are ignored because they aren't valid in the
    first place. (Maybe its a bug in Anime Lyrics to make these links).
    """
    
    # Remove any anchors with # signs in them. They are for javascript.
            
    # Songs appear to have unique names so that they can reside in the
    # root folder of the album. That root folder has the index.html
    # which we are parsing *right now*, so do not save index.html URLs.
    # Also, URLs with '?' in them are for PHP pages that we do not want.
    if soup_anchor.has_attr('href'):
        href = soup_anchor['href']
        return '#' not in href and '?' not in href and \
            'index.html' not in href and href != '<a' and \
            'http://' not in href and href != '.txt'
    else:
        return False

def get_all_songs_from_albums(error_report):
    """Gets a list of all song URLs from an album page at Anime Lyrics."""
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
    except KeyboardInterrupt:
        raise
    except WindowsError:
        pass
    
    for genre in genres:
        for album in listdir(path_join(DEFAULT_OUTPUT_PATH_AL, genre)):
            filename = normpath(path_join(DEFAULT_OUTPUT_PATH_AL, genre, album,
                'index.html'))
            try:
                with open(filename, 'r') as infile:
                    content = infile.read()
            except IOError:
                # This file does not exist. Ignore it.
                error_report.add_error(
                    'Error reading album {}: {}. Maybe it does not exist?'.
                    format(albums_crawled, filename))
                continue
            albums_crawled += 1
            
            # The file was successfully loaded. Extract all anchor links.
            soup = BeautifulSoup(content)
            anchors = [anchor for anchor in soup('a') \
                if is_song_valid_url(anchor, error_report, quiet)]
            # See if these anchored song pages have kanji lyrics available.
            for anchor in anchors[:]:
                if does_song_have_kanji_lyrics(anchor, error_report, quiet):
                    if SAVE_HTML_VARIANT:
                        # Save the Kanji version of the page too.
                        urls.append(anchor['href'][:anchor['href'].rfind('.')]+\
                            '.jis')
                    else:
                        # Save the print-view version, but remove the old one.
                        # We will have redundant data crawled otherwise because
                        # they store all three text types in the print view.
                        anchors.remove(anchor)
                        urls.append(anchor['href'][:anchor['href'].rfind('.')]+\
                            '.jis.txt')
            if SAVE_HTML_VARIANT:
                urls += [anchor['href'] for anchor in anchors]
            else:
                # Save the print-view versions of the URLs of the remaining
                # anchors. These anchors do not have kanji lyrics. Remove the
                # file extension of the anchor and replace it with .txt
                urls += [anchor['href'][:anchor['href'].rfind('.')] + '.txt' \
                    for anchor in anchors]
            
            if DEBUG_PRINT_DIAGNOSTICS:
                if albums_crawled % DIAGNOSTICS_MULTIPLE == 0:
                    print('Album {}: {}'.format(albums_crawled, filename))
    if DEBUG_PRINT_DIAGNOSTICS:
        print('Got {} song URLs from {} cached album pages.'.format(
            len(urls), albums_crawled))
    return urls
