#!/usr/bin/env python
# encoding=utf8
"""Personal BGG Ratings."""

import argparse
import math
import re
import sys
from datetime import datetime
from functools import cmp_to_key
from operator import itemgetter


import requests
import requests_cache
import xmltodict

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
        version='%(prog)s 6.0.0',
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
    requests_cache.install_cache('data_cache')
    while True:
        data = requests.get(url)
        if not data.status_code == 200 or data.status_code == 202:
            continue
        else:
            break
    return data.text


def bayesian_average(rating, mean, plays, lastPlayed):
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
    days = datetime.now() - datetime.strptime(lastPlayed, "%Y-%m-%d")
    days = days.days
    freshness = bayes_avg/math.log(days+2)
    return freshness

def get_last_play(username,gameID):
    """Get last date user played a game."""
    baseurl = 'https://www.boardgamegeek.com/xmlapi2/'
    url = baseurl + (f"plays?username={username}&id={gameID}")
    data = request_data(url)
    doc = xmltodict.parse(data)
    try:
        lastPlayed = doc['plays']['play'][0]['@date']
    except KeyError:
        lastPlayed =  doc['plays']['play']['@date']
    return lastPlayed

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
    collection = []
    baseurl = 'https://www.boardgamegeek.com/xmlapi2/'
    url = baseurl + (f"collection?username={username}&own=1"
                     '&rated=1&played=1&stats=1')
    data = request_data(url)
    doc = xmltodict.parse(data)
    mean_rating = calculate_mean(doc)
    for game in doc['items']['item']:
        gameId = game['@objectid']
        title = game['name']['#text'].strip()
        player_rating = game['stats']['rating']['@value']
        plays = game['numplays']
        lastPlayed = get_last_play(username,gameId)
        rating = bayesian_average(player_rating, mean_rating, plays, lastPlayed)
        collection.append({'name': title, 'player_rate': player_rating,
                           'rating': rating, 'plays': plays, 'last_played': lastPlayed})

    collection = multikeysort(collection, ['rating', 'name'])

    return collection


def display_top_games(collection, count, detailed):
    """Display top games based on ratings then number of plays."""
    if detailed:
        print(f"{'Rank':<6}{'Rating':<8}{'Weighted':<11}{'Plays':<7}" \
              f"{'Last Played':<13}{'Game':<100}")
    else:
        print(f"{'Rank':<5}{'Game':<100}")
    rank = 1
    rgx = re.compile('[%s]' % 'b\'\"')
    for game in collection:
        if detailed:
            print(f"{rank:<6d}{float(game['player_rate']):<8.1f}" \
                  f"{float(game['rating']):<11.4f}" \
                  f"{game['plays']:<7}{game['last_played']:<13}{rgx.sub('',game['name']):<100s}")
        else:
            print(f"{rank:<5d}{rgx.sub('',game['name']):<100s}")
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
