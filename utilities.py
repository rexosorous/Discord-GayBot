# standard libraries
from random import randint
from sys import stdout
from os import listdir
import logging
import json

# dependencies
from fuzzywuzzy import fuzz



commands = ('```'
            'bot COMMANDS\n'
            'note: all commands must be preceeded by "gay ". ex: "gay help"\n'
            'note: all instances of <user> can be pings with @ or name shorthands. ex: "gay mock @GayZach" is the same as "gay mock j-zach"\n'
            'github link: https://github.com/rexosorous/discord-bot\n\n'
            'help\n'
            'checknicknames\n'
            'mock <user>\n'
            'yikes <user>\n'
            'checkyikes <user>\n'
            'bruh\n'
            'emoji <emoji name>                 <emoji name> should not be surrounded by colons\n'
            'quote <user> <lines>               <lines> is optional and should be the number of lines to quote\n'
            'soundboard <clip name>             <clip name> should be optained from gay checksoundboard\n'
            'cliproulette\n'
            'checksoundboard\n'
            'soundboardstats <field> <order>    <field> should be the field to sort by. fields: "name", "soundboard", "roulette", or "normal"\n'
            '                                   <order> "asc" or "desc"\n'
            'phasmophobia <audio sequence>      <audio sequence> should be "footsteps", "door", "moan", or "heartbeat"'
            'remind <time> <msg> (<users>)      <time> must follow this format: YYYY/MM/DD hh:mm to set an absolute date\n'
            '                                   <time> must follow this format: hh:mm to set a relative time. ex: 2:30 would be 2.5 hours from now\n'
            '                                   <msg> is the message you want the bot to say when it reminds you and is optional\n'
            '                                   <users> who you want the bot to ping and MUST be surrounded by () and is optional\n'
            'checkreminders\n'
            'removereminder <id>                <id> should be obtained from checkreminders'
            'stop\n'
            'leave\n'
            'scan\n'
            '```')



def load_file(filename: str) -> dict:
    with open(filename, 'r') as file:
        contents = json.load(file)
    return contents



def get_logger():
    '''
    initializes logger
    '''
    logger = logging.getLogger('gaybot')
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler(filename='gaybot.log', encoding='utf-8', mode='a')
    file_handler.setFormatter(logging.Formatter('%(asctime)s:   %(message)s'))
    console_handler = logging.StreamHandler(stdout)
    console_handler.setFormatter(logging.Formatter('%(asctime)s:   %(message)s'))
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger



def get_max_word_count() -> int:
    '''
    returns the longest word count of all soundboard files
    '''
    max_word_count = 0
    for file_name in listdir('soundboard/'):
        word_count = len(file_name.split(' '))
        if word_count > max_word_count:
            max_word_count = word_count
    return max_word_count



def get_clip(search: str) -> str:
    selected_clip = ''
    best_confidence = 0

    for clip in listdir('soundboard/'):
        fixed_clip = clip[:-4]
        confidence = fuzz.token_set_ratio(search, fixed_clip)
        if confidence > best_confidence:
            best_confidence = confidence
            selected_clip = clip

    return f'soundboard/{selected_clip}'



def mock_msg(original: str) -> str:
    '''
    randomizes the capitalization of every character in a string
    '''
    mocked = ''
    for char in original:
        if randint(0, 1) == 1:
            mocked += char.upper()
        else:
            mocked += char.lower()
    return mocked