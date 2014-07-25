#!usr/bin/env python
# coding: utf-8

from os.path import splitext, dirname
import codecs
from utils_and_defs import *
from bs4 import BeautifulSoup, element

__doc__ = """Turns crawled pages from Anime Lyrics into indexable pages.

It recursively looks in the directory of crawled pages and takes all
non-"index.html" pages and turns them into a format Lucene can
understand.
"""

def remove_ws_between_jp_text(jp_text):
    """Removes the whitespace from between Japanese text.
    
    This function quits if it tries too many substitutions.
    
    @param jp_text: A Unicode string to parse.
    @returns: The processed Unicode string.
    """
    
    num_substitutions = 0
    reached_steady_state = False
    while not reached_steady_state and num_substitutions < 10:
        new_text = spaced_jp_regex.sub(remove_inner_spaces, jp_text)
        reached_steady_state = new_text == jp_text
        jp_text = new_text
        num_substitutions += 1
    return jp_text

def get_kanji_lines(kanji_div):
    """Takes the div tag as a string and extracts the lines of text.
    
    Retrieve the text using something like str(beautiful_soup_instance('div')).
    
    @param kanji_div: The BeautifulSoup instance's div tag with lyrics in it.
    @returns: A string with the lyrics of the song in it.
    """
    
    # Anime Lyrics separated their lyrics with <br> tags.
    lines = kanji_div.split('<br/>')
    # From the first line, remove the initial <div> tag.
    lines[0] = lines[0][lines[0].find('>') + 1:]
    # Similarly, remove the closing </div> tag from the last line.
    lines[-1] = lines[-1][:lines[-1].rfind('</div')]
    # Do bulk processing on all lines.
    for i in range(len(lines)):
        line = lines[i]
        # Remove the newlines put in the Anime Lyrics HTML source files.
        line = line.replace('\n', '')
        # Remove all whitespace before and after the lines.
        line = line.strip()
        # In order to have consistent regex calculations, make the string utf8.
        line = unicode(line, encoding='utf8', errors='strict')
        # Continually remove whitespace between Japanese characters until
        # either we reach a steady state or we have done too many substitutions.
        line = remove_ws_between_jp_text(line)
        lines[i] = line
    # Put all lines into one string for writing out to disk.
    return '\n'.join(lines)

def get_song_name(soup):
    """Gets the song name from a BeautifulSoup instance."""
    # The song name is in the h1 tag.
    # A <br> tag separates transliterations from translations.
    return ' - '.join([content.strip() for content in soup.h1.contents \
        if type(content) is element.NavigableString])

def get_artist(plain_text):
    """Gets the artist (performer) of a song from plain text."""
    # The song performer is within a <br> tag and starts with either
    # "Performed by: " or "Performance:".
    performer = ''
    performer_idx = plain_text.find('Perform')
    colon_idx = 0
    if performer_idx >= 0:
        # Find the colon after Performer. If it's too far or not there, maybe
        # there was no performer for the song in the first place.
        colon_idx = plain_text.find(':', performer_idx)
        if colon_idx < 0 or colon_idx - performer_idx > 30:
            # The colon is not there or is far away. Try finding "by" instead.
            colon_idx = plain_text.find('by', performer_idx)
            if colon_idx > 0:
                # We have found "by", but make the strip() operation not
                # capture the "y" of "by". Increment the index.
                colon_idx += 1
        if colon_idx >= 0 and colon_idx - performer_idx <= 30:
            # Extract the perfomer's name from beyond the colon.
            performer = plain_text[colon_idx + 1 : plain_text.find(
                '\n', colon_idx)].strip()
    return performer

def write_doc(fullpath, song_name, artist, textformat, lyrics, error_report):
    """Writes out the indexable document for Lucene."""
    # Find out where to put the doc. Start by removing the relative addressing.
    rel_addr = fullpath[len(DEFAULT_OUTPUT_PATH_AL) + len(path_sep):]
    # Regenerate the URL to the Anime Lyrics page.
    # Replace Windows backslashes with slashes for URLs.
    url = HOME_PAGE_AL + rel_addr.replace('\\', '/')
    # Prepend the directory of the indexable pages to the output path.
    # Then, remove the file's extension and replace it with .txt .
    docpath = splitext(path_join(OUTPUT_PATH_AL_INDEXABLE, rel_addr))[0]+'.txt'
    create_dir_recursively(dirname(docpath))
    
    with codecs.open(docpath, 'w', encoding='utf8') as outfile:
        outfile.write('\n'.join([url, song_name, artist, textformat, lyrics]))

def make_indexable_doc(fullpath, error_report):
    with open(fullpath, 'r') as infile:
        text = infile.read()
    soup = BeautifulSoup(text)
    
    song_name = get_song_name(soup)
    artist = get_artist(text)
    
    # Remove all anchors that surround kanji.
    while soup.a is not None:
        soup.a.replace_with(soup.a.string)
    
    # Get the div tag containing all kanji text.
    try:
        kanji_markup = soup('div', id='kanji')
    except IndexError:
        error_report.add_report('Could not find kanji text in {}.'.format(
            fullpath))
        return
    
    lyrics = get_kanji_lines(str(kanji_markup))
    write_doc(fullpath, song_name, artist, 'J', lyrics, error_report)

def main(error_report):
    """Finds all crawled pages and makes indexable pages from them.
    
    It also generates a list of the files the indexer must look at.
    """
    create_dir_recursively(OUTPUT_PATH_AL_INDEXABLE)
    
    num_songs = 0
    song_index = []
    for genre in TOP_LEVEL_PAGES[0:1]:
        genre_path = normpath(path_join(DEFAULT_OUTPUT_PATH_AL, genre))
        for album in listdir(genre_path)[0:5]:
            album_path = normpath(path_join(genre_path, album))
            # Get all songs. The index page is not a song.
            songs = [normpath(path_join(album_path, song)) for \
                song in listdir(album_path) if song != 'index.html']
            # TEMPORARY: Parse only SJIS pages.
            songs = [song for song in songs if song.endswith('.jis')]
            for song in songs:
                num_songs += 1
                if DEBUG_PRINT_DIAGNOSTICS:
                    print('Making doc {} for {}.'.format(num_songs, song))
                make_indexable_doc(song, error_report)
            song_index += [song[ABOVE_CRAWLED_DIR:] for song in songs]
    
    with open(DOC_LIST_FILENAME, 'w') as outfile:
        outfile.write('\n'.join(song_index))

if __name__ == '__main__':
    error_report = ErrorReport()
    try:
        main(error_report)
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
