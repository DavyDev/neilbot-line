# What to do after cloning

- `python -m venv _env`
- `pip install -r requirements.txt`
- `ngrok http 5000`
- `gunicorn --bind 127.0.0.1:5000 server:app`