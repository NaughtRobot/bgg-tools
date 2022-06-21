#!/usr/bin/env python
# encoding=utf8
"""Personal BGG Ratings."""

import argparse
import re
import sys
from datetime import date
from functools import cmp_to_key
from operator import itemgetter


import requests
import requests_cache
import xmltodict
from dateutil.relativedelta import relativedelta

sys.getdefaultencoding()


def get_args():
    """Gather command line arguments or display help."""
    parser = argparse.ArgumentParser(description='BGG Game Rankings',
                                     add_help=False)
    parser.add_argument('-h', '--help', action='help',
                        default=argparse.SUPPRESS,
                        help='Show this help message and exit.')
    parser.add_argument(
        '-v',
        '--version',
        action='version',
        version='%(prog)s 0.0.1',
        help="Show program's version number")
    parser.add_argument('-u', '--user', help='BGG username',
                        required=True, metavar='')
    parser.add_argument('-m', '--mounths', help='Last X months',
                        required=True, metavar='')    
    parser.add_argument('-c', '--count', help='Number of results',
                        required=False, metavar='', default=12)                
    parser.add_argument('-d', '--detailed', help='Detailed output',
                        required=False, action='store_true')
    return parser.parse_args()


def request_data(url):
    """Request data from boardgamegeek."""   
    requests_cache.install_cache('data_cache')
    while True:
        data = requests.get(url)
        if not data.status_code == 200 or "try again later" in data.text:
            continue
        else:
            break
    return data.text


def get_pervious_date(months_in_past):
    """Return a date X months in the past."""
    pervious_date = date.today() + relativedelta(months=-months_in_past)
    return str(pervious_date)


def multikeysort(items, columns):
    """Sort dictionary based on multiple keys."""
    comparers = [((itemgetter(col[1:].strip()), 1) if col.startswith('-') else
                  (itemgetter(col.strip()), -1)) for col in columns]

    def comparer(left, right):
        for _fn, mult in comparers:
            result = ((_fn(left) > _fn(right)) - (_fn(left) < _fn(right)))
            if result:
                return mult * result
        return None

    return sorted(items, key=cmp_to_key(comparer))


def get_plays(username):
    """Get user's played games over X months."""
    months = 12
    min_date = get_pervious_date(months)
    plays = []
    baseurl = 'https://www.boardgamegeek.com/xmlapi2/'
    url = baseurl + (f"plays?username={username}&mindate={min_date}")
    data = request_data(url)
    doc = xmltodict.parse(data)

for game in doc['plays']['play']:
    title = game['item']['@name'].strip()
    quantity = int(game['@quantity'])
    print(f"{title} - {quantity}")
    if any(plays):
        next((game.update(plays=game['plays'] + 1) for game in plays if game['name'] == title), plays.append({'name':title,'plays':quantity}))
    else:
        plays.append({'name':title,'plays':quantity})

    plays = multikeysort(play_quantity, ['count', 'name'])

    return plays

def display_hot_games(plays):
    rank = 1
    count = 10
    rgx = re.compile('[%s]' % 'b\'\"')
    for play in plays:
        print(f"{rank:<5d}{rgx.sub('',play['name']):<100s}")
        if count:
            if rank < int(count):
                rank += 1
            else:
                sys.exit()
        else:
            rank += 1

if __name__ == "__main__":
    ARGS = get_args()
    display_hot_games(get_plays(ARGS.user))
