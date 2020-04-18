# utf-8 enconding
from __future__ import unicode_literals
from dotenv import load_dotenv
load_dotenv()

import os, sys, logging, json
from random import randint
from . import richmenu, omongo
from logging.handlers import SysLogHandler
from flask import Flask, request, abort, render_template, send_from_directory
from flask_pymongo import PyMongo
from werkzeug.middleware.proxy_fix import ProxyFix
from linebot import (
    LineBotApi, WebhookHandler)
from linebot.exceptions import (
    LineBotApiError, InvalidSignatureError)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, SourceUser, SourceGroup,
    SourceRoom, TemplateSendMessage, ConfirmTemplate, MessageAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URIAction,
    PostbackAction, DatetimePickerAction, CameraAction, CameraRollAction,
    LocationAction, CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage, UnfollowEvent,
    FollowEvent, JoinEvent, LeaveEvent, BeaconEvent, MemberJoinedEvent,
    MemberLeftEvent, FlexSendMessage, BubbleContainer, ImageComponent,
    BoxComponent, TextComponent, SpacerComponent, IconComponent,
    ButtonComponent, SeparatorComponent, QuickReply, QuickReplyButton,
    ImageSendMessage)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_ACCESS_TOKEN', None)
if channel_secret is None:
    print('Please specify CHANNEL_SECRET in env variables')
    sys.exit(1)
if channel_access_token is None:
    print('Please specify ACCESS_TOKEN in env variables')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
myhandler = WebhookHandler(channel_secret)
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1, x_proto=1)
mongo1 = PyMongo(app, uri= os.environ['MONGODB_URI_1']).db

syslog = SysLogHandler(address=('logs2.papertrailapp.com', 51603))
formatter = logging.Formatter(
    '%(asctime)s neilbot: %(message)s', datefmt='%b %d %H:%M:%S')
syslog.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(syslog)
logger.setLevel(logging.INFO)

#logger.info("neilbot is watching..")
print('neilbot initialized and now monitoring..')

def add_to_mongo():
    #Step 2: Create sample data
    names = ['Kitchen', 'Animal', 'State', 'Tastey', 'Big', 'City',
            'Fish', 'Pizza', 'Goat', 'Salty', 'Sandwich', 'Lazy', 'Fun']
    company_type = ['LLC', 'Inc', 'Company', 'Corporation']
    company_cuisine = ['Pizza', 'Bar Food', 'Fast Food',
                    'Italian', 'Mexican', 'American', 'Sushi Bar', 'Vegetarian']
    for x in range(1, 501):
        business = {
            'name': names[randint(0, (len(names)-1))] + ' ' + names[randint(0, (len(names)-1))] + ' ' + company_type[randint(0, (len(company_type)-1))],
            'rating': randint(1, 5),
            'cuisine': company_cuisine[randint(0, (len(company_cuisine)-1))]
        }
        #Step 3: Insert business object directly into MongoDB via isnert_one
        result = mongo1.reviews.insert_one(business)
        #Step 4: Print to the console the ObjectID of the new document
        print('Created {0} of 500 as {1}'.format(x, result.inserted_id))
    #Step 5: Tell us that you are done
    print('finished creating 500 business reviews')

def read_mongo(mongoid, collection):
    if collection not in mongoid.list_collection_names():
        print('[ERROR] collection "{}" doesn\'t exist!.'.format(collection))
        return
    else:
        for x in mongoid[collection].find():
            print(x)
        return

@app.errorhandler(Exception)
def index(e):
    return render_template("index.html")


@app.route('/hook', methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    #logger.info("Request body: " + body)
    #print("Request body: " + body)

    # handle webhook body
    try:
        myhandler.handle(body, signature)
    except LineBotApiError as e:
        print("Got exception from LINE Messaging API: %s\n" % e.message)
        for m in e.error.details:
            print("  %s: %s" % (m.property, m.message))
        print("\n")
    except InvalidSignatureError:
        abort(400)
    return 'OK'


@app.route('/static/<path:path>')
def send_static_content(path):
    return send_from_directory('static', path)


@myhandler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    text = event.message.text

    if text == 'profile':
        if isinstance(event.source, SourceUser):
            profile = line_bot_api.get_profile(event.source.user_id)
            line_bot_api.reply_message(
                event.reply_token, [
                    TextSendMessage(
                        text='Display name: ' + profile.display_name),
                    TextSendMessage(
                        text='Status message: ' + str(profile.status_message))
                ])
            print("[LOG] user id {} requested profile information".format(
                event.source.user_id))
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(
                    text="Bot can't use profile API without user ID"))
    elif text == 'bye':
        if isinstance(event.source, SourceGroup):
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text='Leaving group'))
            line_bot_api.leave_group(event.source.group_id)
            print('[LOG] bot left group id {}'.format(event.source.group_id))
        elif isinstance(event.source, SourceRoom):
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text='Leaving group'))
            line_bot_api.leave_room(event.source.room_id)
            print('[LOG] bot left group id {}'.format(event.source.room_id))
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="Bot can't leave from 1:1 chat"))
    elif text == 'image':
        # url = request.url_root + ''
        url = 'https://cdn.glitch.com/39356d38-9cd4-48d5-9eec-3ca49387a195%2Flogo.png?v=1586956803590'
        line_bot_api.reply_message(event.reply_token, ImageSendMessage(
            url, url))
        print('[LOG] bot just sent an image to user')
    else:
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.message.text))
        print('[LOG] bot sent message to user: "{}"'.format(text))
        if omongo.read(mongo1, 'userList') != 0:
            if mongo1['userList'].count_documents({'userID': event.source.user_id}) is 0:
                profile = line_bot_api.get_profile(event.source.user_id)
                tmp = {'userID': event.source.user_id,
                        'name': profile.display_name}
                omongo.add(mongo1, 'userList', tmp)
                print('registered user successfully')
            else: print('user already registered!')
        else:
            profile = line_bot_api.get_profile(event.source.user_id)
            tmp = {'userID': event.source.user_id,
                   'name': profile.display_name}
            omongo.add(mongo1, 'userList', tmp)
            print('registered user successfully')


@myhandler.add(FollowEvent)
def handle_follow(event):
    line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text='Got follow event'))
    print('[LOG] user {} just followed the bot.'.format(event.source.user_id))


@myhandler.add(UnfollowEvent)
def handle_unfollow(event):
    print('[LOG] user {} unfollowed the bot.'.format(event.source.user_id))


@myhandler.add(JoinEvent)
def handle_join(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='Hi! The bot joined the ' + event.source.type))
    print('[LOG] bot just join group id {}'.format(event.source.group_id))


@myhandler.add(LeaveEvent)
def handle_leave(event):
    print('[LOG] bot left group id {}'.format(event.source.room_id))


@myhandler.add(PostbackEvent)
def handle_postback(event):
    if event.postback.data == 'ping':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='pong'))
    elif event.postback.data == 'datetime_postback':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.postback.params['datetime']))
    elif event.postback.data == 'date_postback':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.postback.params['date']))


@myhandler.add(MemberJoinedEvent)
def handle_member_joined(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='Got memberJoined event. event={}'.format(event)))


@myhandler.add(MemberLeftEvent)
def handle_member_left(event):
    print("Got memberLeft event")
