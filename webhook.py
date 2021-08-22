import asyncio
import aiohttp
from aiohttp import web
import json
from config import api_key
from templates import *

API_URL = 'https://api.telegram.org/bot%s/sendMessage' % api_key


def get_user_dict():
    user_dict = {}
    list_file = open("user_list.txt", "r")
    lines = list_file.readlines()
    for line in lines:
        temp_list = line.split(",")
        user_dict[temp_list[0]] = temp_list
    list_file.close()
    return user_dict


def allow_send(user, data):
    if user[2] == "1":
        if data.get('object_kind', "None") == "None":
            if user[3] == "1":
                return True
        elif (data["object_kind"] == "push") and (user[3] == "1"):
            return True
        elif (data["object_kind"] == "wiki_page") and (user[6] == "1"):
            return True
        elif (data["object_kind"] == "tag_push") and (user[3] == "1"):
            return True
        elif (data["object_kind"] == "issue") and (user[5] == "1"):
            return True
        elif (data["object_kind"] == "note") and (user[5] == "1"):
            return True
        elif (data["object_kind"] == "merge_request") and (user[5] == "1"):
            return True
        elif (data["object_kind"] == "pipeline") and (user[4] == "1"):
            return True
        elif (data["object_kind"] == "build") and (user[4] == "1"):
            return True
        else:
            return False
    else:
        return False


def parser(data):
    if data.get('object_kind', "None") == "None":
        return parser_push_gogs(data)
    elif data["object_kind"] == "push":
        return parser_push_gitlab(data)
    elif data["object_kind"] == "wiki_page":
        return parser_wiki(data)
    elif data["object_kind"] == "tag_push":
        return parser_tag_push(data)
    elif data["object_kind"] == "issue":
        return parser_issue(data)
    elif data["object_kind"] == "note":
        return parser_note(data)
    elif data["object_kind"] == "merge_request":
        return parser_merge_request(data)
    elif data["object_kind"] == "pipeline":
        return parser_pipeline(data)
    elif data["object_kind"] == "build":
        return parser_build(data)


async def handler(request):
    data = await request.json()
    print(data)
    text = parser(dict(data))
    headers = {
        'Content-Type': 'application/json'
    }
    user_dict = get_user_dict()
    for user in user_dict:
        if allow_send(user_dict[user], data) and (text != ''):
            message = {
                'disable_web_page_preview': True,
                'parse_mode': 'HTML',
                'chat_id': user_dict[user][1],
                'text': text
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(API_URL,
                                        data=json.dumps(message),
                                        headers=headers) as resp:
                    if resp.status != 200:
                        print(f"Error sending message to Telegram: {resp}")
    return web.Response(status=200)


async def init_app(loop):
    app = web.Application(middlewares=[])
    app.router.add_post('/api/v1', handler)
    return app

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        app = loop.run_until_complete(init_app(loop))
        web.run_app(app, host='0.0.0.0', port=23456)
    except Exception as e:
        print('Error create server: %r' % e)
    finally:
        pass
    loop.close()