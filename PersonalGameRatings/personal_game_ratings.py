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
        version='%(prog)s 4.0.0',
        help="Show program's version number")
    parser.add_argument('-u', '--user', help='BGG username',
                        required=True, metavar='')
    parser.add_argument('-c', '--count', help='Number of results',
                        required=False, metavar='')
    parser.add_argument('-d', '--detailed', help='Detailed output',
                        required=False, action='store_true')
    return parser.parse_args()


def request_data(url):
    """Request data from boardgamegeek."""
    while True:
        data = requests.get(url)
        if not data.status_code == 200 or "try again later" in data.text:
            continue
        else:
            break
    return data.text


def bayesian_average(rating, mean, plays):
    """Bayesian average for game based on number of plays.

    BA = R*(p+m)*M/(p+m)
    R = rating for the game.
    p = number of plays of the game.
    m = minimum number of plays of the game.
    M = mean rating for all games rated and owned.
    """
    minimum_plays = 5
    rating, mean, plays = float(rating), float(mean), float(plays)
    bayes_avg = (rating * plays + minimum_plays * mean / plays + minimum_plays)
    return bayes_avg


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
    for game in doc['items']['item']:
        title = game['name']['#text'].strip()
        player_rating = game['stats']['rating']['@value']
        plays = game['numplays']
        rating = bayesian_average(player_rating, mean_rating, plays)
        COLLECTION.append({'name': title, 'player_rate': player_rating,
                           'rating': rating, 'plays': plays})

    collection = multikeysort(COLLECTION, ['rating', 'name'])

    return collection


def display_top_games(collection, count, detailed):
    """Display top games based on ratings then number of plays."""
    if detailed:
        print("{0:<5}{1:<7}{2:<7}{3:<100}\n".format('Rank', 'Rating', 'Plays',
                                                    'Game'))
    else:
        print("{0:<5}{1:<100}\n".format('Rank', 'Game'))

    rank = 1
    for game in collection:
        if detailed:
            print(
                "{0:<5d}{1:<7.1f}{2:<7}{3:<100s}".format(
                    rank, float(
                        game['player_rate']), int(
                        game['plays']), str(
                        game['name']).strip('b').strip('\'').strip('\"')))
        else:
            print("{0:<5d}{1:<100s}".format(rank,
                  game['name'].strip('b').strip('\'').strip('\"')))
        if count:
            if rank < int(count):
                rank += 1
            else:
                sys.exit()
        else:
            rank += 1


if __name__ == "__main__":
    ARGS = get_args()
    display_top_games(get_collection(ARGS.user), ARGS.count, ARGS.detailed)
