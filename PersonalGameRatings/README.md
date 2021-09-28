# Personal Game Ratings
I love top ten list and board games. I'm also lazy and lacked a way to easily generate a top ten list of my favorite board games. Top ten list are naturally subjective to the individual and I'm looking more a little more empirical evidence as to why my number seven game is higher on the list then my number eight game. To accomplish this, I've combined my game ratings from [Board Game Geek](https://boardgamegeek.com/) with the number of logged plays I have for each game to create the most accurate top ten board game list for me. The assumption here is that if I really like a game, then I'm going to continue to play the game. Thus the higher I rate the game and the more I play the game the higher it is on my top ten list. Simple right?!

## Bayesian Calculation
Here is the formula used to calculate the Bayesian average for a game. It accounts for my game rating on BGG and the number of plays I've logged.

    BA = R*(p+m)*M/(p+m)

    R = rating for the game.
    p = number of plays of the game.
    m = minimum number of plays of the game.
    M = mean rating for all games rated and owned.

For the minimum number of play, I have initially set the value to five. As I log more game plays this value may be raised. As it stands now there is some wild variance in a few of my lower ranked games that causes them to appear higher on the top ten list than they should after a single play. With additional plays the list should even out over time. As for now I'm leaving the minimum number of plays set to five.
