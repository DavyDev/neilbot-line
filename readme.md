# Notes to maintainer
[![Build Status](https://travis-ci.org/DavyDev/neilbot-line.svg?branch=master)](https://travis-ci.org/DavyDev/neilbot-line)

- `python -m venv _env`
- `pip install -r requirements.txt`
- `ngrok http 8000`
- `gunicorn run:app --log-file --reload`

Served on [Zeit] or [Heroku]

[zeit]: https://neilbot-line.now.sh
[heroku]: https://neilbot-py.herokuapp.com/hook