# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import sys
import logging
import socket

from logging.handlers import SysLogHandler
from argparse import ArgumentParser
from logdna import LogDNAHandler
from modules import richmenu

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

log = logging.getLogger('logdna')
log.setLevel(logging.INFO)
log.addHandler(LogDNAHandler(os.getenv('LOGDNA', None), {'hostname': 'neilbot', 'index_meta': True}))

syslog = SysLogHandler(address=('logs2.papertrailapp.com', 51603))
format = '%(asctime)s neilbot: %(message)s'
formatter = logging.Formatter(format, datefmt='%b %d %H:%M:%S')
syslog.setFormatter(formatter)

logger = logging.getLogger()
logger.addHandler(syslog)
logger.setLevel(logging.INFO)

def my_handler(type, value, tb):
  logger.exception('Uncaught exception: {0}'.format(str(value)))

# Install exception handler
sys.excepthook = my_handler

logger.info('This is a message')
nofunction() #log an uncaught exception


app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('CHANNEL_SECRET', None)
channel_access_token = os.getenv('ACCESS_TOKEN', None)
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)


@app.route('/hook', methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text)
        )
        log.info('text sent: {}'.format(event.message.text))

    return 'OK'


if __name__ == "__main__":
    log.info("service started..")
    app.run(debug=True)