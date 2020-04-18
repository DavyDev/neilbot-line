# Notes to maintainer
[![Build Status](https://travis-ci.org/DavyDev/neilbot-line.svg?branch=master)](https://travis-ci.org/DavyDev/neilbot-line)

- `python -m venv _env`
- `pip install -r requirements.txt`
- `ngrok http 8000`
- `gunicorn run:app --log-file --reload`

Served on [Zeit] and [Heroku]

## For Users
This bot is still under active development. The core features have no clear purpose yet, since I am still doing some experiments on the capabilities of the [Line Messaging SDK](https://github.com/line/line-bot-sdk-python).

#### Usage
1. Add `@149irafe` as your friend.
2. Try to message him and play around!

[zeit]: https://neilbot-line.now.sh
[heroku]: https://neilbot-py.herokuapp.com/hook