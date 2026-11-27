[![make.fun · news-image-20261127](https://make.fun/badge/news-image-20261127.svg)](https://make.fun/bounty/news-image-20261127?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)
[![rank](https://make.fun/badge/news-image-20261127/prabowo888888-cmyk/news-image-20261127/rank.svg)](https://make.fun/bounty/news-image-20261127/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)
[![reward](https://make.fun/badge/news-image-20261127/prabowo888888-cmyk/news-image-20261127/reward.svg)](https://make.fun/bounty/news-image-20261127?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)

# One Image, One Day: Friday 27 November 2026

This little program paints a single picture of a single day. Run it and you
get a 1024 by 1024 poster that gathers the five world stories that mattered
most on Friday 27 November 2026, so anyone glancing at it can catch up on
the day in a few seconds.

## What the picture shows

The day opens in the Gulf, where a drone strike on an air-defence site in
Kuwait killed two Italian technicians and pulled Iran, Italy and Kuwait into
a sharp diplomatic row. Across the Atlantic, a Thanksgiving storm battered
the United States, forced the postponement of the 100th Macy's parade in
New York and left more than half a million homes without power. In Gaza,
fresh strikes killed ten people while Hamas weighed its response. On the
trade front, Washington rolled out new tariffs of up to 40 percent against
fourteen trading partners. And to close the day on a quieter note, the
World Chess Championship stayed deadlocked as Gukesh and Sindarov drew a
marathon third game.

Each story gets its own row: a number, a small hand-drawn icon, a headline,
and two short lines of context, with the sources listed along the bottom.

## How to run it

The program needs nothing beyond Python 3 itself. There are no extra
packages to install and no network calls while it runs.

```sh
python3 main.py
```

That writes `entry.png` into `/output`. To point it somewhere else, set
`MAKEFUN_OUTPUT_DIR` first:

```sh
MAKEFUN_OUTPUT_DIR=/tmp/out python3 main.py
```

## How the image is drawn

Everything is drawn pixel by pixel with the standard library alone. A tiny
built-in 5 by 7 bitmap font supplies the lettering, simple shapes make up
the icons, and the PNG file is assembled by hand from raw scanlines with
`zlib` compression. Because nothing random and nothing time-based is
involved, running the program twice produces a byte-for-byte identical
file every time.

## Sources

Reuters, BBC, The New York Times, Mint and India Today — as reported on
27 November 2026.
