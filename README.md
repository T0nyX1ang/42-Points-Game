# 42-Points-Game
![42Points](https://github.com/T0nyX1ang/42-Points-Game/workflows/42Points/badge.svg)
[![Maintainability](https://api.codeclimate.com/v1/badges/9502c3fcb954f16254cf/maintainability)](https://codeclimate.com/github/T0nyX1ang/42-Points-Game/maintainability)
[![codecov](https://codecov.io/gh/T0nyX1ang/42-Points-Game/branch/master/graph/badge.svg)](https://codecov.io/gh/T0nyX1ang/42-Points-Game)
![PyPI](https://img.shields.io/pypi/v/42Points)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/42Points)
![PyPI - License](https://img.shields.io/pypi/l/42Points)

Python implementation of the fourty-two points game. 

## Introduction
"42 Points" game is a variation based on the popular and long-lived "24 Points" game. The player should only use addition, subtraction, multiplication, division and parentheses and __five__ integers between 0 and 13 (inclusive) to get 42. It's really simple to understand, as the core of the game still relies on math calculations.

## Design Logic
This package is designed to __work as a core processing part__, providing:
* Problem database
* Problem generation (by user / in database)
* Start / stop the game
* Timer for solutions
* Player statistics
* Equivalent solution detection
* A bunch of APIs and exceptions

This package is not designed to __fully implement everything__ with the game, so the formatting parts should be written by end-users. But don't worry, the API in this package is enough to create whatever you need.

## Usage
As equivalent detection is not a easy issue, we will make several changes to make sure it satisfies our need in the following upgrades. Please just kindly use the latest version.

It's recommended to use `pip`:
```bash
    pip install --upgrade 42Points
```

But building with `setup.py` will also work, as no other third-party dependencies are required for this package.

After you have installed the package, you are almost done. If you want to try it out quickly, just open your IDLE (or something like that) and type:
```py
    from ftptsgame import FTPtsGame
    app = FTPtsGame() # initialize
    app.generate_problem('database') # generate a problem beforehand
    app.start() # start the game
    app.get_current_problem() # show the problem
    app.solve('your solutions') # put forward a solution
    app.get_current_solutions() # show all solutions
    app.stop() # stop the game
```

Well, you can integrate this package into your projects by using just the same way, and you can format problems in all the ways you like.

## License
This package is licensed under the `MIT License`.

## Contribution
Pull requests and issues are warmly welcomed. 
