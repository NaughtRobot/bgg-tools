#!/usr/bin/env python
# encoding=utf8
"""Boardgame Geek Hot Games List."""

import requests
import xmltodict


def request_data(url):
    """Request data from boardgamegeek."""
    data = requests.get(url)
    return data.content

def get_hotness():
    """Return current list of hot games on Board Game Geek."""
    url = "https://www.boardgamegeek.com/xmlapi2/hot?boardgame"
    the_list = xmltodict.parse(request_data(url))
    print(f"{'Rank':<6}{'Year':<7}{'Title':100}")
    count = 1
    for game in the_list['items']['item']:
        if count < 11:
            print(f"{game['@rank']:<6}{game['yearpublished']['@value']:<7}"
                  f"{game['name']['@value']:100}")
            count += 1
        else:
            break

if __name__ == "__main__":
    get_hotness()
       