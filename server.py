# utf-8 enconding
from __future__ import unicode_literals
import os, sys, logging, socket, json, tempfile, errno
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

# create tmp dir for download content
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')
def make_static_tmp_dir():
    try:
        os.makedirs(static_tmp_path)
        logger.info("temp path created at: {}".format(static_tmp_path))
    except OSError as exc:
        logger.info('ERROR make_static_tmp_dir: {}'.format(exc))
        if exc.errno == errno.EEXIST and os.path.isdir(static_tmp_path):
            pass
        else:
            raise


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

@nhandler.add(MessageEvent, message=(ImageMessage, VideoMessage, AudioMessage))
def handle_content_message(event):
    if isinstance(event.message, ImageMessage):
        ext = 'jpg'
    elif isinstance(event.message, VideoMessage):
        ext = 'mp4'
    elif isinstance(event.message, AudioMessage):
        ext = 'm4a'
    else:
        return

    message_content = line_bot_api.get_message_content(event.message.id)
    try:
        with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix=ext + '-', delete=False) as tf:
            for chunk in message_content.iter_content():
                tf.write(chunk)
            logger.info('chunk completed')
            tempfile_path = tf.name
            logger.info('tempfile path is {}'.format(tempfile_path))

        dist_path = tempfile_path + '.' + ext
        dist_name = os.path.basename(dist_path)
        os.rename(tempfile_path, dist_path)


        line_bot_api.reply_message(
            event.reply_token, [
                TextSendMessage(text='Save content.'),
                TextSendMessage(text=request.host_url +
                                os.path.join('static', 'tmp', dist_name))
            ])
    except Exception as e:
        logger.info(e)


@nhandler.add(MessageEvent, message=FileMessage)
def handle_file_message(event):
    message_content = line_bot_api.get_message_content(event.message.id)
    with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix='file-', delete=False) as tf:
        for chunk in message_content.iter_content():
            tf.write(chunk)
        tempfile_path = tf.name

    dist_path = tempfile_path + '-' + event.message.file_name
    dist_name = os.path.basename(dist_path)
    os.rename(tempfile_path, dist_path)

    line_bot_api.reply_message(
        event.reply_token, [
            TextSendMessage(text='Save file.'),
            TextSendMessage(text=request.host_url +
                            os.path.join('static', 'tmp', dist_name))
        ])


if __name__ == "__main__":
    make_static_tmp_dir()
    app.run(debug=False)
