# Fantasy Football Data Analysis

This repo is made to share some scripts that I write every time I'm curious about some data analysis about fantasy football in my league. Most of the scripts will only work on Sleeper. Feel free to use on your own league. Any contributions are welcome!

## Setup
To run the scrips, you should install Python and [pipenv](https://pipenv.pypa.io/en/latest/) and run:
```
pipenv install
```

## Bye advatange analysis
To run:
```
pipenv run python bye-advantage.py
```
And follow the instructions in the terminal

The results should be interpreted as:
- The higher the number of the team, the luckier it is this season with opponent byes
- The lower the number of the team, the unluckier it is this season with opponent byes

The bye advantage points of each team means:
- The sum of all the average pontuation of players of opposing teams in each week that are in byes

Known issues:
- It does not take into account if the player in bye is an starter or not
- Does not work well with DEF and IDP
- It only takes into account the current roster of the team
- Does not work with seasons other than 2023

Will try to fix/make it better. PR welcome!
