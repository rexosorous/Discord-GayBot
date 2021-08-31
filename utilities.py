# standard libraries
from random import randint
from os import listdir

# dependencies
from fuzzywuzzy import fuzz



def get_max_word_count() -> int:
    '''
    Returns the longest word count of all soundboard files

    Returns:
        int
    '''
    max_word_count = 0
    for file_name in listdir('soundboard/'):
        word_count = len(file_name.split(' '))
        if word_count > max_word_count:
            max_word_count = word_count
    return max_word_count



def get_clip(search: str) -> str:
    '''
    Using fuzzywuzzy, searches all the soundboard clips for the closest matching ones

    Returns:
        str: the filename, NOT path/dir
    '''
    selected_clip = ''
    best_confidence = 0

    for clip in listdir('soundboard/'):
        fixed_clip = clip[:-4]
        confidence = fuzz.token_set_ratio(search, fixed_clip)
        if confidence > best_confidence:
            best_confidence = confidence
            selected_clip = clip

    return selected_clip



def mock_msg(original: str) -> str:
    '''
    Randomizes the capitalization of every character in a string

    Returns:
        str
    '''
    mocked = ''
    for char in original:
        if randint(0, 1) == 1:
            mocked += char.upper()
        else:
            mocked += char.lower()
    return mocked