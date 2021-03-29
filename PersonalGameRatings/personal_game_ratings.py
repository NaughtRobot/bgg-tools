#!/usr/bin/env python
# encoding=utf8
"""Personal BGG Ratings."""

import argparse
import sys
from functools import cmp_to_key
from operator import itemgetter

import requests
import xmltodict

sys.getdefaultencoding()

RETRY = 0
COLLECTION = []


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
        version='%(prog)s 3.1.0',
        help="Show program's version \
                        number")
    parser.add_argument('-u', '--user', help='BGG username',
                        required=True, metavar='')
    parser.add_argument('-c', '--count', help='Number of results',
                        required=False, metavar='')
    return parser.parse_args()


def request_data(url):
    """Request data from boardgamegeek."""
    data = requests.get(url)
    return data.content


def weighted_average(rating, mean, plays):
    """Weighted average for game ratings.

    WR = (v/(v+m)*R + (m/(v+m))* C
    R = rating for the game.
    v = number of plays of the game.
    m = minimum number of plays of the game.
    C = mean rating for all games rated and owned.
    """
    rating, mean, plays = float(rating), float(mean), float(plays)
    minimum_plays = 25
    rating = (plays / (plays + minimum_plays)) * rating \
        + (minimum_plays / (plays + minimum_plays)) * mean
    return rating


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


def calculate_mean(collection):
    """Calculate the mean ration for collection."""
    ratings = []
    for game in collection['items']['item']:
        ratings.append(float(game['stats']['rating']['@value']))
    mean = sum(ratings)/len(ratings)
    return mean


def get_collection(username):
    """Get user's collection from BGG."""
    global COLLECTION
    baseurl = 'https://www.boardgamegeek.com/xmlapi2/'
    url = baseurl + ('collection?username={}&own=1'
                     '&rated=1&played=1&stats=1').format(username)
    data = request_data(url)
    doc = xmltodict.parse(data)
    mean_rating = calculate_mean(doc)
    try:
        for game in doc['items']['item']:
            title = game['name']['#text'].encode('utf-8').strip()
            player_rating = game['stats']['rating']['@value']
            plays = game['numplays']
            rating = weighted_average(player_rating, mean_rating, plays)
            COLLECTION.append({'name': title, 'player_rate': player_rating,
                                'rating': rating, 'plays': plays})
    except KeyError:
        global RETRY
        if RETRY < 5:
            RETRY += 1
            get_collection(username)
        else:
            sys.exit(1)

    collection = multikeysort(COLLECTION, ['rating', 'name'])

    return collection


def display_top_games(collection, count):
    """Display top games based on ratings then number of plays."""
    print("{0:<5}{1:<7}{2:<9}{3:<7}{4:<100}".format('Rank', 'Rating',
                                              'Weighted', 'Plays', 'Game'))
    rank = 1
    for game in collection:
        print(
            "{0:<5d}{1:<7.1f}{2:<9.4f}{3:<7}{4:<100s}".format(
                rank, float(
                    game['player_rate']),float(
                    game['rating']), int(
                    game['plays']), str(
                    game['name']).strip('b').strip('\'').strip('\"')))
        if count:
            if rank < int(count):
                rank += 1
            else:
                sys.exit()
        else:
            rank += 1


if __name__ == "__main__":
    ARGS = get_args()
    display_top_games(get_collection(ARGS.user), ARGS.count)
