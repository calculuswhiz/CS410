#!usr/bin/env python
# coding: utf-8

from os.path import splitext, dirname
from utils_and_defs import *
from bs4 import BeautifulSoup

__doc__ = """Turns crawled pages from Anime Lyrics into indexable pages.

It recursively looks in the directory of crawled pages and takes all
non-"index.html" pages and turns them into a format Lucene can
understand.
"""

def get_kanji_lines(kanji_div):
    """Takes the div tag as a string and extracts the lines of text.
    
    Retrieve the text using something like str(beautiful_soup_instance('div')).
    
    @returns: A string with the lyrics of the song in it.
    """
    
    lines = kanji_div.split('<br/>')
    # From the first line, remove the initial <div> tag.
    lines[0] = lines[0][lines[0].find('>') + 1:]
    # Similarly, remove the closing </div> tag from the last line.
    lines[-1] = lines[-1][:lines[-1].rfind('</div')]
    # Remove the newlines put in the Anime Lyrics HTML source files.
    lines = [line.replace('\n', '') for line in lines]
    # Remove the whitespace put in by the Beautiful Soup pretty printer.
    lines = [line.replace(' ', '') for line in lines]
    # Put all lines into one string for writing out to disk.
    return '\n'.join(lines)

def write_doc(fullpath, lyrics, textformat, error_report):
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
    
    song_name = 'Song Name'
    artist = 'Artist'
    with open(docpath, 'w') as outfile:
        outfile.write('\n'.join([url, song_name, artist, textformat, lyrics]))

def make_indexable_doc(fullpath, error_report):
    if DEBUG_PRINT_DIAGNOSTICS:
        print('Making doc for {}.'.format(fullpath))
    
    with open(fullpath, 'r') as infile:
        soup = BeautifulSoup(infile.read())
    
    # Remove all anchors that surround kanji.
    decomposing = True
    while decomposing:
        try:
            while soup.a is not None:
                soup.a.replace_with(soup.a.string)
            decomposing = False
        except AttributeError:
            decomposing = False
    
    # Get the div tag containing all kanji text.
    try:
        kanji_markup = soup('div', id='kanji')
    except IndexError:
        error_report.add_report('Could not find kanji text in {}.'.format(
            fullpath))
        return
    
    lyrics = get_kanji_lines(str(kanji_markup))
    write_doc(fullpath, lyrics, 'J', error_report)

def main(error_report):
    """Finds all crawled pages and makes indexable pages from them.
    
    It also generates a list of the files the indexer must look at.
    """
    create_dir_recursively(OUTPUT_PATH_AL_INDEXABLE)
    
    song_index = []
    for genre in TOP_LEVEL_PAGES[0:1]:
        genre_path = normpath(path_join(DEFAULT_OUTPUT_PATH_AL, genre))
        for album in listdir(genre_path)[0:3]:
            album_path = normpath(path_join(genre_path, album))
            # Get all songs. The index page is not a song.
            songs = [normpath(path_join(album_path, song)) for \
                song in listdir(album_path) if song != 'index.html']
            # TEMPORARY: Parse only SJIS pages.
            songs = [song for song in songs if song.endswith('.jis')]
            for song in songs:
                make_indexable_doc(song, error_report)
            song_index += songs
    
    if DEBUG_PRINT_DIAGNOSTICS:
        print(len(song_index), song_index[:3])

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
