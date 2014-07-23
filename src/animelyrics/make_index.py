#!usr/bin/env python
# coding: utf-8

from utils_and_defs import *

__doc__ = """Turns crawled pages from Anime Lyrics into indexable pages.

It recursively looks in the directory of crawled pages and takes all
non-"index.html" pages and turns them into a format Lucene can
understand.
"""

def make_indexable_doc(fullpath, error_report):
    pass

def main(error_report):
    """Finds all crawled pages and makes indexable pages from them.
    
    It also generates a list of the files the indexer must look at.
    """
    create_dir_recursively(OUTPUT_PATH_AL_INDEXABLE)
    
    song_index = []
    for genre in TOP_LEVEL_PAGES:
        genre_path = normpath(path_join(DEFAULT_OUTPUT_PATH_AL, genre))
        for album in listdir(genre_path):
            album_path = normpath(path_join(genre_path, album))
            # Get all songs. The index page is not a song.
            songs = [normpath(path_join(album_path, song)) for \
                song in listdir(album_path) if song != 'index.html']
            song_index += songs
    
    if DEBUG_PRINT_DIAGNOSTICS:
        print(len(song_index), song_index[:3])

if __name__ == '__main__':
    main(ErrorReport())
