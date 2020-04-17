# utf-8 enconding
from __future__ import unicode_literals
import os, sys, logging, socket, json
from logging.handlers import SysLogHandler
from argparse import ArgumentParser
from modules import richmenu
from flask import Flask, request, abort, render_template
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    LineBotApiError, InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage, VideoMessage, AudioMessage,
    FileMessage
)

syslog = SysLogHandler(address=('logs2.papertrailapp.com', 51603))
formatter = logging.Formatter('%(asctime)s neilbot: %(message)s', datefmt='%b %d %H:%M:%S')
syslog.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(syslog)
logger.setLevel(logging.INFO)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('CHANNEL_SECRET', None)
channel_access_token = os.getenv('ACCESS_TOKEN', None)
if channel_secret is None:
    print('Please specify CHANNEL_SECRET in env variables')
    sys.exit(1)
if channel_access_token is None:
    print('Please specify ACCESS_TOKEN in env variables')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
nhandler = WebhookHandler(channel_secret)
app = Flask(__name__)
logger.info("neilbot is watching..")


# importing words.json file
with open('res/json/words.json') as f:
    wordsMsg = json.load(f)


@app.errorhandler(Exception)
def index(e):
    return render_template("index.html")

@app.route('/hook', methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    logger.info("Request body: " + body)

    # handle webhook body
    try:
        nhandler.handle(body, signature)
    except LineBotApiError as e:
        print("Got exception from LINE Messaging API: %s\n" % e.message)
        for m in e.error.details:
            print("  %s: %s" % (m.property, m.message))
        print("\n")
    except InvalidSignatureError:
        abort(400)
    return 'OK'


@nhandler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text=event.message.text))
    logger.info('text sent: {}'.format(event.message.text))


if __name__ == "__main__":
    app.run(debug=False)
