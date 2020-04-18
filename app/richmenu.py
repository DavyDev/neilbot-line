import os
from dotenv import load_dotenv
from linebot import LineBotApi
from linebot.models import (
    RichMenu, RichMenuSize, RichMenuArea, RichMenuBounds,
    MessageAction, PostbackTemplateAction
)

load_dotenv()
channel_access_token = os.getenv('LINE_ACCESS_TOKEN', None)
line_bot_api = LineBotApi(channel_access_token)

def createNew(image='res/img/logo.png'):
    result = ''
    try:
        # define a new richmenu
        rich_menu_to_create = RichMenu(
            size = RichMenuSize(width=2500, height=843),
            selected = True,
            name = 'Bot Menu',
            chat_bar_text = 'Tap Here',
            areas=[
                RichMenuArea(
                    bounds=RichMenuBounds(x=0, y=0, width=1250, height=843),
                    action=MessageAction(text='REMOVE')
                ),
                RichMenuArea(
                    bounds=RichMenuBounds(x=1250, y=0, width=1250, height=843),
                    action=MessageAction(text='NEXT')
                )
            ]
        )
        richMenuId = line_bot_api.create_rich_menu(rich_menu=rich_menu_to_create)
        print('New richMenu created: '+richMenuId)        
        # upload an image for rich menu
        try:
            with open(image, 'rb') as f:
                line_bot_api.set_rich_menu_image(richMenuId, 'image/png', f)
            result = 'Success upload image '
        except Exception as e:
            result = 'Failed to upload image: '+str(e)
            return result
        # set the default rich menu
        line_bot_api.set_default_rich_menu(richMenuId)
        result += 'and set ' + str(richMenuId) + ' as default'
    except Exception as e:
        result = str(e)
    return result

def formatAll():
    rich_menu_list = line_bot_api.get_rich_menu_list()
    for rich_menu in rich_menu_list:
      line_bot_api.delete_rich_menu(rich_menu.rich_menu_id)
    print('All rich menus are deleted successfully.')

def listAll():
    rich_menu_list = line_bot_api.get_rich_menu_list()
    if (len(rich_menu_list)==0):
      print('No rich menu found')
      return
    for rich_menu in rich_menu_list:
      print(rich_menu.rich_menu_id)
      
def whichDefault():
    try:
      print('Default rich menu: {}'.format(line_bot_api.get_default_rich_menu()))
    except:
      print("No default rich menu")